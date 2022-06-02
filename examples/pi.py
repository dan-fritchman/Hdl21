""" 
# Phase Interpolator Example 
"""

from enum import Enum, auto

import hdl21 as h


@h.bundle
class QuadClock:
    """ # Quadrature Clock Bundle 
    Includes four 90-degree-separated phases. """

    class Roles(Enum):
        # Clock roles: source or sink
        SOURCE = auto()
        SINK = auto()

    # The four quadrature phases, all driven by SOURCE and consumed by SINK.
    ck0, ck90, ck180, ck270 = h.Signals(4, src=Roles.SOURCE, dest=Roles.SINK)


Inv = h.ExternalModule(
    name="Inv",
    port_list=[h.Input(name="i"), h.Output(name="z"),],
    desc="Generic Inverter",
)
TriInv = h.ExternalModule(
    name="TriInv",
    port_list=[h.Input(name="i"), h.Input(name="en"), h.Output(name="z"),],
    desc="Generic Tri-State Inverter",
)
Flop = h.ExternalModule(
    name="Flop",
    port_list=[h.Input(name="d"), h.Input(name="clk"), h.Output(name="q"),],
    desc="Generic Rising-Edge D Flip Flop",
)
Latch = h.ExternalModule(
    name="Latch",
    port_list=[h.Input(name="d"), h.Input(name="clk"), h.Output(name="q"),],
    desc="Generic Active High Level-Sensitive Latch",
)


@h.paramclass
class WeightInvParams:
    weight = h.Param(dtype=int, desc="Weight")


WeightInv = h.ExternalModule(
    name="WeightInv",
    port_list=[h.Input(name="i"), h.Output(name="z"),],
    desc="Weighting Inverter",
    paramtype=WeightInvParams,
)


@h.paramclass
class PhaseWeighterParams:
    wta = h.Param(dtype=int, desc="Weight of Input A")
    wtb = h.Param(dtype=int, desc="Weight of Input B")


@h.generator
def PhaseWeighter(p: PhaseWeighterParams) -> h.Module:
    """ # Phase-Weighter
    Drives a single output with two out-of-phase inputs `a` and `b`, 
    with weights dictates by params `wta` and `wtb`. """

    @h.module
    class PhaseWeighter:
        # IO Ports
        a, b = h.Inputs(2)
        out = h.Output()
        mix = h.Signal(desc="Internal phase-mixing node")

    # Give it a shorthand name for these manipulations
    P = PhaseWeighter

    if p.wta > 0:  # a-input inverter
        P.inva = WeightInv(WeightInvParams(weight=p.wta))(i=P.a, z=P.mix)
    if p.wtb > 0:  # b-input inverter
        P.invb = WeightInv(WeightInvParams(weight=p.wtb))(i=P.b, z=P.mix)

    # Output inverter, with the combined size of the two inputs
    P.invo = WeightInv(WeightInvParams(weight=p.wta + p.wtb))(i=P.mix, z=P.out)

    return PhaseWeighter


@h.paramclass
class PiParams:
    """ Phase Interpolator Parameters """

    nbits = h.Param(dtype=int, default=5, desc="Resolution, or width of select-input.")


@h.generator
def PhaseGenerator(p: PiParams) -> h.Module:
    """ # Phase Generator (Generator) (Get it?) 
    
    Takes a primary input `QuadClock` and interpolates to produce 
    an array of equally-spaced output phases. """

    PhaseGen = h.Module()
    ckq = PhaseGen.ckq = QuadClock(
        role=QuadClock.Roles.SINK, port=True, desc="Quadrature input"
    )
    phases = PhaseGen.phases = h.Output(
        width=2 ** p.nbits, desc="Array of equally-spaced phases"
    )

    if p.nbits != 5:
        msg = f"Yeah we know that's a parameter, but this is actually hard-coded to 5 bits for now"
        raise ValueError(msg)

    # Generate a set of PhaseWeighters and output phases for each pair of quadrature inputs
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck0, b=ckq.ck90, out=phases[index]),
        )
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = 8 + wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck90, b=ckq.ck180, out=phases[index]),
        )
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = 16 + wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck180, b=ckq.ck270, out=phases[index]),
        )
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = 24 + wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck270, b=ckq.ck0, out=phases[index]),
        )

    return PhaseGen


@h.generator
def OneHotEncode5to32(_: h.HasNoParams) -> h.Module:
    """ 5 to 32b One-Hot Encoder """
    m = h.Module()
    m.inp = h.Input(width=5, desc="Binary-Encoded Input")
    m.out = h.Output(width=32, desc="One-Hot-Encoded Output")
    # FIXME! the actual contents
    return m


@h.generator
def PhaseSelector(p: PiParams) -> h.Module:
    """ # Phase Selector Mux """

    @h.module
    class PhaseSelector:
        # IO Interface
        phases = h.Input(width=2 ** p.nbits, desc="Array of equally-spaced phases")
        sel = h.Input(width=p.nbits, desc="Selection input")
        out = h.Output(width=1, desc="Clock output")

        # Internal Contents
        encoder = OneHotEncode5to32()(inp=sel)
        invs = 32 * TriInv()(i=phases, en=encoder.out, z=out)

    return PhaseSelector


@h.generator
def PhaseInterp(p: PiParams) -> h.Module:
    """ Phase Interpolator Generator """

    @h.module
    class PhaseInterp:
        # IO Interface
        ckq = QuadClock(role=QuadClock.Roles.SINK, port=True, desc="Quadrature input")
        sel = h.Input(width=p.nbits, desc="Selection input")
        out = h.Output(width=1, desc="Clock output")

        # Internal Signals
        phases = h.Signal(width=2 ** p.nbits, desc="Array of equally-spaced phases")

        # Instantiate the phase-generator and phase-selector
        phgen = PhaseGenerator(p)(ckq=ckq, phases=phases)
        phsel = PhaseSelector(p)(phases=phases, sel=sel, out=out)

    return PhaseInterp


# "Main" Script Content
import sys

h.netlist(h.to_proto(PhaseInterp()), dest=sys.stdout)

