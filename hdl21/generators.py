""" 
# Hdl21 Built-In Generators Library 
"""

import copy
from dataclasses import asdict, replace
from typing import Optional, Tuple, Union

from . import primitives
from .primitives import MosType, MosVth
from .generator import generator
from .module import Module
from .params import paramclass, Param
from .signal import Signal
from .instantiable import Instantiable


@paramclass
class MosParams:
    """ Mos Series-Stack Generator Parameters """

    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)
    nser = Param(dtype=int, desc="Number of series fingers", default=1)
    npar = Param(dtype=int, desc="Number of parallel fingers", default=1)
    tp = Param(dtype=MosType, desc="MosType (PMOS/NMOS)", default=MosType.NMOS)
    vth = Param(dtype=MosVth, desc="Threshold voltage specifier", default=MosVth.STD)

    def __post_init_post_parse__(self):
        """ Value Checks """
        if self.w <= 0:
            raise ValueError(f"MosParams with invalid width {self.w}")
        if self.l <= 0:
            raise ValueError(f"MosParams with invalid length {self.l}")
        if self.npar <= 0:
            raise ValueError(
                f"MosParams with invalid number parallel fingers {self.npar}"
            )
        if self.nser <= 0:
            raise ValueError(
                f"MosParams with invalid number series fingers {self.nser}"
            )


@generator
def Mos(params: MosParams) -> Module:
    """ Mos Series-Stack Generator 
    Generates a `Module` including `nser` identical series instances of unit-Mos `primitives.Mos`.  
    Unit-Mos gate and bulk ports are connected in parallel. """

    # Extract the number of series fingers
    nser = params.nser
    # Extract the remaining params for the unit transistor
    unit_params = asdict(params)
    unit_params.pop("nser")
    unit_params = primitives.Mos.Params(**unit_params)
    # Create the Primitive unit-cell
    unit_xtor = primitives.Mos(unit_params)

    # Initialize our stack-module
    m = Module()
    # Copy the unit-cell ports
    for p in primitives.Mos.port_list:
        m.add(copy.copy(p))

    # Add instances, starting at the source-side
    inst = m.add(name="unit0", val=unit_xtor(s=m.s, g=m.g, b=m.b))
    for iser in range(1, nser):
        prev_inst = inst
        inst = m.add(name=f"unit{iser}", val=unit_xtor(s=prev_inst.d, g=m.g, b=m.b))
    # Finally connect the drain to the last instance
    inst.d = m.d
    # And return the module
    return m


@generator
def Nmos(params: MosParams) -> Module:
    """ Nmos Generator. A thin wrapper around `hdl21.generators.Mos` """
    return Mos(replace(params, tp=MosType.NMOS))


@generator
def Pmos(params: MosParams) -> Module:
    """ Pmos Constructor. A thin wrapper around `hdl21.generators.Mos` """
    return Mos(replace(params, tp=MosType.PMOS))


@paramclass
class SeriesParParams:
    """ Series-Parallel Generator Parameters """

    # Required
    unit = Param(dtype=Instantiable, desc="Unit cell")
    series_conns = Param(
        dtype=Tuple[Union[Signal, str], Union[Signal, str]],
        desc="Ports or port-names of `unit` to be connected in series",
    )
    # Optional
    nser = Param(dtype=int, desc="Number of series instances", default=1)
    npar = Param(dtype=int, desc="Number of parallel stacks", default=1)


@generator
def SeriesPar(params: SeriesParParams) -> Module:
    """ Series-Parallel Generator 
    Arrays `params.npar` copies of `params.nser` series-stacked Instances of unit-cell `params.unit`. 
    The generated `Module` includes the same ports as `unit`. 
    The two series-connected ports of `unit` are specified by parameter two-tuple `series_conns`. 
    All other ports of `unit` are wired in parallel, and exposed as ports of the generated `Module`. """

    unit = params.unit

    # Initialize our stack-module
    m = Module()
    # Copy the unit-cell ports
    for p in unit.ports.values():
        m.add(copy.copy(p))

    # Check for validity of the series-ports
    if isinstance(params.series_conns[0], str):
        ser0 = m.ports.get(params.series_conns[0], None)
    elif isinstance(params.series_conns[0], Signal):
        ser0 = params.series_conns[0]
    else:  # Unreachable
        raise TypeError
    if isinstance(params.series_conns[1], str):
        ser1 = m.ports.get(params.series_conns[1], None)
    elif isinstance(params.series_conns[1], Signal):
        ser1 = params.series_conns[1]
    else:  # Unreachable
        raise TypeError
    if ser0 is None or ser1 is None:
        raise ValueError(f"SeriesPar: unit does not have ports {params.series_conns}")

    # Extract all the parallel-connected ports
    par_conns = {
        port.name: port
        for port in unit.ports.values()
        if port.name not in params.series_conns
    }

    for ipar in range(params.npar):
        # Add instances, starting at the `series_conns[0]`-side
        inst = unit(**par_conns).connect(ser0.name, ser0)
        inst = m.add(name=f"unit_{ipar}_0", val=inst)
        for iser in range(1, params.nser):
            prev_inst = inst
            inst = unit(**par_conns)
            inst.connect(ser0.name, prev_inst.port_ref(ser1.name))
            inst = m.add(name=f"unit_{ipar}_{iser}", val=inst)
        # Finally connect the last series-port to the last instance
        inst.connect(ser1.name, ser1)
    # And return the module
    return m


def Wrapper(m: Module) -> Module:
    """ 
    # Module Wrapper Creator

    Adds a `Module` hierarchy layer around argument-`Module` `m`. 
    Creates an `Instance` of `m` and clones its ports, connecting each. 
    
    Note: `Wrapper` is generally aways more helpful when the returned `Module` is modified after the fact. 
    Hence while `Wrapper` is a *function that returns a `Module`*, it is *not* an `hdl21.Generator`, 
    which cache and unique-name their results. 
    Callers of `Wrapper` are therefore responsible for considerations such as unique naming. 
    """

    # FIXME: find this function a home with a less-confusing name!

    # Initialize our wrapper-module
    wrapper = Module(name=f"{m.name}Wrapper")

    # Copy the unit-cell ports
    for p in m.io.values():
        wrapper.add(copy.copy(p))

    # Create a connections-dict mirroring them
    conns = {port.name: port for port in wrapper.io.values()}

    # Create the inner instance
    wrapper.add(name="inner", val=m(**conns))

    # And return the wrapper
    return wrapper
