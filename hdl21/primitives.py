"""
# Hdl21 Primitive Modules

Primitives are leaf-level Modules typically defined not by users, 
but by simulation tools or device fabricators. 
Prominent examples include MOS transistors, diodes, resistors, and capacitors. 

"""

from dataclasses import asdict, replace
from enum import Enum
from typing import Optional, Callable, Any, Union
from .params import paramclass, Param
from .generator import Generator, generator
from .module import Module
from .signal import Port


class Primitive:
    # Am I an anything? We'll see.
    # So far not; these are built of Modules and Generators.
    ...


class MosType(Enum):
    """ NMOS/PMOS Type Enumeration """

    NMOS = 0
    PMOS = 1


class MosVth(Enum):
    """ MOS Threshold Enumeration """

    STD = 2
    # Moar coming soon!


@paramclass
class MosParams:
    """ MOS Transistor Parameters """

    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)
    nser = Param(dtype=int, desc="Number of series fingers", default=1)
    npar = Param(dtype=int, desc="Number of parallel fingers", default=1)
    tp = Param(dtype=MosType, desc="MosType (PMOS/NMOS)", default=MosType.NMOS)
    vth = Param(dtype=MosVth, desc="Threshold voltage specifier", default=MosVth.STD)


class MosModule(Module):
    """ Primitive Module for all MOS Transistors """

    d = Port()
    g = Port()
    s = Port()
    b = Port()


@generator
def Mos(params: MosParams) -> Module:
    return MosModule


@generator
def Nmos(params: MosParams) -> Module:
    return Mos(replace(params, tp=MosType.NMOS))


@generator
def Pmos(params: MosParams) -> Module:
    return Mos(replace(params, tp=MosType.PMOS))


@paramclass
class DiodeParams:
    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)

    # FIXME: will likely want a similar type-switch, at least eventually
    # tp = Param(dtype=Tbd!, desc="Diode type specifier")


class DiodeModule(Module):
    """ Primitive Module for Diodes """

    p = Port()
    n = Port()


@generator
def Diode(params: DiodeParams) -> Module:
    return DiodeModule


# Common alias(es)
D = Diode


@paramclass
class ResistorParams:
    r = Param(dtype=float, desc="Resistance (ohms)")


class ResistorModule(Module):
    """ Primitive Module for Ideal Resistors """

    p = Port()
    n = Port()


@generator
def Resistor(params: ResistorParams) -> Module:
    return ResistorModule


# Common aliases
R = Res = Resistor


@paramclass
class CapacitorParams:
    c = Param(dtype=float, desc="Capacitance (F)")


class CapacitorModule(Module):
    """ Primitive Module for Ideal Capacitors """

    p = Port()
    n = Port()


@generator
def Capacitor(params: CapacitorParams) -> Module:
    return CapacitorModule


# Common aliases
C = Cap = Capacitor


@paramclass
class InductorParams:
    l = Param(dtype=float, desc="Inductance (H)")


class InductorModule(Module):
    """ Primitive Module for Ideal Inductors """

    p = Port()
    n = Port()


@generator
def Inductor(params: InductorParams) -> Module:
    return CapacitorModule


# Common alias(es)
L = Inductor


@paramclass
class ShortParams:
    layer = Param(dtype=Optional[int], desc="Metal layer", default=None)
    w = Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = Param(dtype=Optional[int], desc="Length in resolution units", default=None)


class ShortModule(Module):
    """ Primitive Module for Short-Circuit Ties Between Signals """

    p = Port()
    n = Port()


@generator
def Short(params: ShortParams) -> Module:
    """ Primitive Module for Short-Circuit Ties Between Signals """
    return ShortModule

