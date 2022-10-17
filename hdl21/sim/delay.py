""" 
# Delay Measurements and Sims 

The many, many-th iteration of taking a `Module` comprised of digital logic, 
setting the states of all but one input, stepping the other, and measuring the delay(s) 
to each of its outputs. 
"""

from copy import copy
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import vlsir.spice_pb2 as vsp
from vlsirtools.spice import sim_data as sd, SimResultUnion

# Local Imports
from ..module import Module
from ..signal import Signal, Port, Visibility, PortDir, _copy_to_internal
from ..instantiable import Instantiable
from ..prefix import Prefix
from ..primitives import Vdc, Vpu, Cap
from .data import ParamVal, Sim, SimAttr


class LogicState(Enum):
    LOW = False
    HIGH = True


class Transition(Enum):
    RISING = "rising"
    FALLING = "falling"


@dataclass
class DelaySimParams:
    dut: Instantiable  # The design under test

    primary_input: Signal  # The primary input to be tested
    other_inputs: Dict[str, LogicState]  # Logical values of other inputs

    input_trans: Transition  # Primary-input transition direction

    vlo: ParamVal  # Logic-low level
    vhi: ParamVal  # Logic-high level

    # Mapping from supply (names) to values
    supplies: Dict[str, ParamVal] = field(default_factory=dict)
    # List of ground signals (names)
    grounds: List[Signal] = field(default_factory=list)

    # Capacitance on each output, keyed by name
    load_caps: Dict[str, ParamVal] = field(default_factory=dict)
    # Default capacitance on each output, if not specified in `load_caps`
    default_load_cap: ParamVal = 1 * Prefix.ATTO

    trf: ParamVal = 1 * Prefix.PICO  # Input rise / fall time
    tstop: ParamVal = 1 * Prefix.NANO  # Sim stop time
    tstep: Optional[ParamVal] = 1 * Prefix.PICO  # Recommended sim timestep

    # Sadly we don't really know how to pass these into `Sim` yet, without some help here.
    pathsep: str = "."  # Hierarchical path separator
    # Expression delimiters, opening and closing. Pair of single quotes by default.
    expr_delim: Tuple[str, str] = ("'", "'")

    # Additional simulation attributes (options, saves, etc)
    attrs: List[SimAttr] = field(default_factory=list)


@dataclass
class DelaySimResult:
    """Results from a `DelaySim`"""

    # Per-output delays, keyed by output signal name
    delays: Dict[str, Optional[float]]


def delays(p: DelaySimParams, opts: Optional[vsp.SimOptions] = None) -> DelaySimResult:
    """Create and run a delay `Sim`.

    Executes four discrete steps, all defined in this module:

    * `create_sim`
    * `run` the generated `Sim`
    * `get_meas` is a short step to gather the measurement dictionary. It will (should) eventually disappear.
    * `collect_result`

    Each individually for cases needing to "get in between" them.
    """
    sim = create_sim(p)
    results = sim.run(opts=opts)
    meas = get_meas(results)
    return collect_result(p, meas)


def create_sim(p: DelaySimParams) -> Sim:
    """Create a delay `Sim`"""

    # Create the testbench `Module` and `Sim` input
    tb = Module(name=f"{p.dut.name}Tb")
    tb.vss = Port(width=1)
    sim = Sim(tb=tb, attrs=p.attrs)
    # Add the primary transient analysis
    tran = sim.tran(
        tstop=p.tstop, tstep=p.tstep, name=f"tran_delay_{p.primary_input.name}"
    )

    # Instantiate the DUT
    tb.dut = p.dut()

    # Create the primary input Signal
    sig = copy(p.primary_input)
    if sig.width != 1:
        raise RuntimeError(f"Unsupported `Delay` sim for bus input {inp}")
    sig.vis = Visibility.INTERNAL
    sig.direction = PortDir.NONE
    tb.add(sig)
    tb.dut.connect(sig.name, sig)

    # Create its pulse-source
    (v1, v2) = (p.vlo, p.vhi) if p.input_trans == Transition.RISING else (p.vhi, p.vlo)
    vpulse_params = Vpu.Params(
        v1=v1,
        v2=v2,
        delay=0 * Prefix.UNIT,
        period=2 * Prefix.UNIT,
        rise=p.trf,
        fall=p.trf,
        width=1 * Prefix.UNIT,
    )
    vpulse = Vpu(vpulse_params)(p=sig, n=tb.vss)
    tb.add(vpulse, name=f"v{p.primary_input.name}")

    # Add a measurement of the inital primary-input crossing time
    cross = "rise" if p.input_trans == Transition.RISING else "fall"
    sim.meas(
        analysis=tran,
        name=f"tcross_primary_input",
        expr=f"when V(xtop{p.pathsep}{p.primary_input.name})={p.expr_delim[0]}vdd/2{p.expr_delim[1]} {cross}=1",  # FIXME: simulator-specific
    )

    for gndsig in p.grounds:
        # Make each ground connection to test-bench VSS
        tb.dut.connect(gndsig.name, tb.vss)

    for vname, vval in p.supplies.items():
        # Create and connect each supply voltage
        # And add a voltage-source instance to drive it
        sig = p.dut.get(vname)
        if sig is None:
            raise RuntimeError(f"Invalid Supply {vname} in creating delay for {p.dut}")
        sig = tb.add(_copy_to_internal(sig))
        tb.add(Vdc(Vdc.Params(dc=vval))(p=sig, n=tb.vss), name=f"v{sig.name}")
        tb.dut.connect(sig.name, sig)

    dut_inputs = [s for s in p.dut.ports.values() if s.direction == PortDir.INPUT]
    for inp in dut_inputs:
        if inp == p.primary_input:
            continue  # Skip the primary input

        # Create a Signal for each DUT input
        inp = tb.add(_copy_to_internal(inp))
        if inp.width != 1:
            raise RuntimeError(f"Unsupported `Delay` sim for bus input {inp}")
        tb.dut.connect(inp.name, inp)

        # Get its logic state
        state = p.other_inputs.get(inp.name, None)
        if state is None:
            raise ValueError(f"No LogicState defined for input {inp}")
        if state == LogicState.HIGH:
            vdc = p.vhi
        elif state == LogicState.LOW:
            vdc = p.vlo
        else:
            raise ValueError(f"Invalid LogicState {state} for Input {inp}")

        # And add a voltage-source instance to drive it
        tb.add(Vdc(Vdc.Params(dc=vdc))(p=inp, n=tb.vss), name=f"v{inp.name}")

    # Create everything associated with each output - load caps and measurements
    dut_outputs = [s for s in p.dut.ports.values() if s.direction == PortDir.OUTPUT]
    for out in dut_outputs:
        out = tb.add(_copy_to_internal(out))
        if out.width != 1:
            raise RuntimeError(f"Unsupported `Delay` sim for bus output {inp}")
        tb.dut.connect(out.name, out)

        # Sort out the load capacitance value, from either the signal-specific dict, or the default value
        c = p.load_caps.get(out.name, p.default_load_cap)

        # Add a load cap instance
        tb.add(Cap(Cap.Params(c=c))(p=out, n=tb.vss), name=f"c{out.name}")

        # Add a delay measurement
        sim.meas(
            analysis=tran,
            name=f"tcross_{out.name}",
            expr=f"when V(xtop{p.pathsep}{out.name})={p.expr_delim[0]}vdd/2{p.expr_delim[1]} cross=1",  # FIXME: simulator-specific
        )
        sim.meas(
            analysis=tran,
            name=f"tdelay_{out.name}",
            expr=f"PARAM={p.expr_delim[0]}tcross_{out.name}-tcross_primary_input{p.expr_delim[1]}",  # FIXME: simulator-specific
        )

    # Aaaaaaand return the sim already!
    return sim


def collect_result(
    p: DelaySimParams, meas: Dict[str, Optional[float]]
) -> DelaySimResult:
    """
    Collect measured output delays
    After simulation has run and data has been pulled back into memory,
    extract the delay value for each of `p.module`'s outputs.
    """
    delays = {}
    dut_outputs = [s for s in p.dut.ports.values() if s.direction == PortDir.OUTPUT]
    for out in dut_outputs:
        out_meas = meas.get(f"tdelay_{out.name}", None)
        if out_meas is None:
            delays[out.name] = None
        else:
            try:
                delays[out.name] = float(out_meas)
            except:
                delays[out.name] = None
    return DelaySimResult(delays)


def get_meas(results: SimResultUnion) -> Dict[str, Optional[float]]:
    """Get the `measurements` dict from either of the `VlsirTools` sim-results types.
    FIXME: this should get pushed down to `VlsirTools`."""

    if isinstance(results, sd.SimResult):
        return results.an[0].measurements
    if isinstance(results, vsp.SimResult):
        return results.an[0].tran.measurements
    raise TypeError
