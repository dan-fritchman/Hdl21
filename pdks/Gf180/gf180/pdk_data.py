""" 

# Hdl21 + Global Foundries 180nm MCU PDK Modules and Transformations 

Defines a set of `hdl21.ExternalModule`s comprising the essential devices of the Global Foundries 180nm open-source PDK, '
and an `hdl21pdk.netlist` method for converting process-portable `hdl21.Primitive` elements into these modules. 

The complete 180nm design kit includes hundreds of devices. A small subset are targets for conversion from `hdl21.Primitive`. 
They include: 

* 

Remaining devices can be added to user-projects as `hdl21.ExternalModule`s, 
or added to this package via pull request.  

"""

# Std-Lib Imports
from copy import deepcopy
from pathlib import Path
from dataclasses import field
from typing import Dict, Tuple, Optional, List, Any
from types import SimpleNamespace

# PyPi Imports
from pydantic.dataclasses import dataclass

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import MILLI, µ, p
from hdl21.pdk import PdkInstallation, Corner, CmosCorner
from hdl21.primitives import (
    Mos,
    PhysicalResistor,
    PhysicalCapacitor,
    Diode,
    Bipolar,
    ThreeTerminalResistor,
    ThreeTerminalCapacitor,
    MosType,
    MosVth,
    MosFamily,
    BipolarType,
    MosParams,
    PhysicalResistorParams,
    PhysicalCapacitorParams,
    DiodeParams,
    BipolarParams,
)

FIXME = None  # FIXME: Replace with real values!
PDK_NAME = "gf180"

# Vlsirtool Types to ease downstream parsing
from vlsirtools import SpiceType


@h.paramclass
class MosParams:
    """# GF180 Mos Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1 * µ)
    nf = h.Param(dtype=h.Scalar, desc="Number of Fingers", default=1)
    # This unfortunate naming is to prevent conflicts with base python.
    As = h.Param(
        dtype=h.Scalar,
        desc="Source Area",
        default=h.Literal("int((nf+2)/2) * w/nf * 0.18u"),
    )

    ad = h.Param(
        dtype=h.Scalar,
        desc="Source Area",
        default=h.Literal("int((nf+2)/2) * w/nf * 0.18u"),
    )

    pd = h.Param(
        dtype=h.Scalar,
        desc="Drain Perimeter",
        default=h.Literal("2*int((nf+1)/2) * (w/nf + 0.18u)"),
    )
    ps = h.Param(
        dtype=h.Scalar,
        desc="Source Perimeter",
        default=h.Literal("2*int((nf+2)/2) * (w/nf + 0.18u)"),
    )
    nrd = h.Param(
        dtype=h.Scalar, desc="Drain Resistive Value", default=h.Literal("0.18u / w")
    )
    nrs = h.Param(
        dtype=h.Scalar, desc="Source Resistive Value", default=h.Literal("0.18u / w")
    )
    sa = h.Param(
        dtype=h.Scalar,
        desc="Spacing between Adjacent Gate to Drain",
        default=0,
    )
    sb = h.Param(
        dtype=h.Scalar,
        desc="Spacing between Adjacent Gate to Source",
        default=0,
    )
    sd = h.Param(
        dtype=h.Scalar,
        desc="Spacing between Adjacent Drain to Source",
        default=0,
    )
    mult = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


# FIXME: keep this alias as prior versions may have used it
GF180MosParams = MosParams


@h.paramclass
class GF180ResParams:
    """# GF180 Generic Resistor Parameters"""

    r_width = h.Param(dtype=h.Scalar, desc="Width in PDK Units (m)", default=1 * µ)
    r_length = h.Param(dtype=h.Scalar, desc="Length in PDK Units (m)", default=1 * µ)
    m = h.Param(dtype=h.Scalar, desc="Length in PDK Units (m)", default=1)


@h.paramclass
class GF180CapParams:
    """# GF180 Capacitor Parameters"""

    c_width = h.Param(dtype=h.Scalar, desc="Width in PDK Units (m)", default=10 * µ)
    c_length = h.Param(dtype=h.Scalar, desc="Length in PDK Units (m)", default=10 * µ)
    m = h.Param(dtype=h.Scalar, desc="Parallel Multiplier", default=1)


@h.paramclass
class GF180DiodeParams:
    """# GF180 Diode Parameters"""

    area = h.Param(dtype=h.Scalar, desc="Area in PDK Units (m²)", default=1 * p)
    pj = h.Param(
        dtype=h.Scalar, desc="Junction Perimeter in PDK units (m)", default=4 * µ
    )
    m = h.Param(dtype=h.Scalar, desc="Parallel Multiplier", default=1)


@h.paramclass
class GF180BipolarParams:
    """# GF180 Bipolar Parameters"""

    m = h.Param(dtype=h.Scalar, desc="Parallel Multiplier", default=1)


@h.paramclass
class GF180LogicParams:
    """# GF180 Logic Parameters"""

    m = h.Param(dtype=h.Scalar, desc="Parallel Multiplier", default=1)


def xtor_module(modname: str) -> h.ExternalModule:
    """Transistor module creator, with module-name `name`.
    If optional `MosKey` `key` is provided, adds an entry in the `xtors` dictionary."""

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Mos {modname}",
        port_list=deepcopy(h.Mos.port_list),
        paramtype=MosParams,
        spicetype=SpiceType.SUBCKT,
    )

    return mod


def res_module(modname: str, numterminals: int) -> h.ExternalModule:
    """Resistor Module creator"""

    num2device = {2: PhysicalResistor, 3: ThreeTerminalResistor}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Res{numterminals} {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=GF180ResParams,
    )

    return mod


def diode_module(modname: str) -> h.ExternalModule:
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Diode {modname}",
        port_list=deepcopy(Diode.port_list),
        paramtype=GF180DiodeParams,
        spicetype=SpiceType.DIODE,
    )

    return mod


def cap_module(modname: str, params: h.Param) -> h.ExternalModule:
    """Capacitor Module creator"""
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Cap {modname}",
        port_list=deepcopy(PhysicalCapacitor.port_list),
        paramtype=params,
    )

    return mod


FourTerminalBipolarPorts = [
    h.Port(name="c"),
    h.Port(name="b"),
    h.Port(name="e"),
    h.Port(name="s"),
]


def bjt_module(modname: str, num_terminals=3) -> h.ExternalModule:
    num2device = {3: Bipolar.port_list, 4: FourTerminalBipolarPorts}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK {num_terminals}-terminal BJT {modname}",
        port_list=deepcopy(num2device[num_terminals]),
        paramtype=GF180BipolarParams,
    )

    return mod


def logic_module(
    modname: str,
    family: str,
    terminals: List[str],
) -> h.ExternalModule:

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{family} {modname} Logic Circuit",
        port_list=[h.Port(name=i) for i in terminals],
        paramtype=GF180LogicParams,
    )

    return mod
