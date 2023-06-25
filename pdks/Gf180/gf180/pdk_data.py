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


def _xtor_module(modname: str) -> h.ExternalModule:
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


def _res_module(modname: str, numterminals: int) -> h.ExternalModule:
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


def _diode_module(modname: str) -> h.ExternalModule:
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Diode {modname}",
        port_list=deepcopy(Diode.port_list),
        paramtype=GF180DiodeParams,
        spicetype=SpiceType.DIODE,
    )

    return mod


def _cap_module(modname: str, params: h.Param) -> h.ExternalModule:
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


def _bjt_module(modname: str, num_terminals=3) -> h.ExternalModule:
    num2device = {3: Bipolar.port_list, 4: FourTerminalBipolarPorts}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK {num_terminals}-terminal BJT {modname}",
        port_list=deepcopy(num2device[num_terminals]),
        paramtype=GF180BipolarParams,
    )

    return mod


def _logic_module(
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


# Individuate component types
MosKey = Tuple[str, h.MosType]
BjtKey = Tuple[str, h.BipolarType]

xtors: Dict[MosKey, h.ExternalModule] = {
    ("PFET_3p3V", MosType.PMOS, MosFamily.CORE): _xtor_module("pfet_03v3"),
    ("NFET_3p3V", MosType.NMOS, MosFamily.CORE): _xtor_module("nfet_03v3"),
    ("NFET_6p0V", MosType.NMOS, MosFamily.IO): _xtor_module("nfet_06v0"),
    ("PFET_6p0V", MosType.PMOS, MosFamily.IO): _xtor_module("pfet_06v0"),
    ("NFET_3p3V_DSS", MosType.NMOS, MosFamily.NONE): _xtor_module("nfet_03v3_dss"),
    ("PFET_3p3V_DSS", MosType.PMOS, MosFamily.NONE): _xtor_module("pfet_03v3_dss"),
    ("NFET_6p0V_DSS", MosType.NMOS, MosFamily.NONE): _xtor_module("nfet_06v0_dss"),
    ("PFET_6p0V_DSS", MosType.PMOS, MosFamily.NONE): _xtor_module("pfet_06v0_dss"),
    ("NFET_6p0V_NAT", MosType.NMOS, MosFamily.NONE): _xtor_module("nfet_06v0_nvt"),
}

ress: Dict[str, h.ExternalModule] = {
    "NPLUS_U": _res_module("nplus_u", 3),
    "PPLUS_U": _res_module("pplus_u", 3),
    "NPLUS_S": _res_module("nplus_s", 3),
    "PPLUS_S": _res_module("pplus_s", 3),
    "NWELL": _res_module("nwell", 3),
    "NPOLYF_U": _res_module("npolyf_u", 3),
    "PPOLYF_U": _res_module("ppolyf_u", 3),
    "NPOLYF_S": _res_module("npolyf_s", 3),
    "PPOLYF_S": _res_module("ppolyf_s", 3),
    "PPOLYF_U_1K": _res_module("ppolyf_u_1k", 3),
    "PPOLYF_U_2K": _res_module("ppolyf_u_2k", 3),
    "PPOLYF_U_1K_6P0": _res_module("ppolyf_u_1k_6p0", 3),
    "PPOLYF_U_2K_6P0": _res_module("ppolyf_u_2k_6p0", 3),
    "PPOLYF_U_3K": _res_module("ppolyf_u_3k", 3),
    "RM1": _res_module("rm1", 2),
    "RM2": _res_module("rm2", 2),
    "RM3": _res_module("rm3", 2),
    "TM6K": _res_module("tm6k", 2),
    "TM9K": _res_module("tm9k", 2),
    "TM11K": _res_module("tm11k", 2),
    "TM30K": _res_module("tm30k", 2),
}

diodes: Dict[str, h.ExternalModule] = {
    "ND2PS_3p3V": _diode_module("diode_nd2ps_03v3"),
    "PD2NW_3p3V": _diode_module("diode_pd2nw_03v3"),
    "ND2PS_6p0V": _diode_module("diode_nd2ps_06v0"),
    "PD2NW_6p0V": _diode_module("diode_pd2nw_06v0"),
    "NW2PS_3p3V": _diode_module("diode_nw2ps_03v3"),
    "NW2PS_6p0V": _diode_module("diode_nw2ps_06v0"),
    "PW2DW": _diode_module("diode_pw2dw"),
    "DW2PS": _diode_module("diode_dw2ps"),
    "Schottky": _diode_module("sc_diode"),
}

bjts: Dict[BjtKey, h.ExternalModule] = {
    "PNP_10p0x0p42": _bjt_module("pnp_10p00x00p42"),
    "PNP_5p0x0p42": _bjt_module("pnp_05p00x00p42"),
    "PNP_10p0x10p0": _bjt_module("pnp_10p00x10p00"),
    "PNP_5p0x5p0": _bjt_module("pnp_05p00x05p00"),
    "NPN_10p0x10p0": _bjt_module("npn_10p00x10p00", 4),
    "NPN_5p0x5p0": _bjt_module("npn_05p00x05p00", 4),
    "NPN_0p54x16p0": _bjt_module("npn_00p54x16p00", 4),
    "NPN_0p54x8p0": _bjt_module("npn_00p54x08p00", 4),
    "NPN_0p54x4p0": _bjt_module("npn_00p54x04p00", 4),
    "NPN_0p54x2p0": _bjt_module("npn_00p54x02p00", 4),
}

caps: Dict[str, h.ExternalModule] = {
    "MIM_1p5fF": _cap_module("cap_mim_1f5fF", GF180CapParams),
    "MIM_1p0fF": _cap_module("cap_mim_1f0fF", GF180CapParams),
    "MIM_2p0fF": _cap_module("cap_mim_2f0fF", GF180CapParams),
    "PMOS_3p3V": _cap_module("cap_pmos_03v3", GF180CapParams),
    "NMOS_6p0V": _cap_module("cap_nmos_06v0", GF180CapParams),
    "PMOS_6p0V": _cap_module("cap_pmos_06v0", GF180CapParams),
    "NMOS_3p3V": _cap_module("cap_nmos_03v3", GF180CapParams),
    "NMOS_Nwell_3p3V": _cap_module("cap_nmos_03v3_b", GF180CapParams),
    "PMOS_Pwell_3p3V": _cap_module("cap_pmos_03v3_b", GF180CapParams),
    "NMOS_Nwell_6p0V": _cap_module("cap_nmos_06v0_b", GF180CapParams),
    "PMOS_Pwell_6p0V": _cap_module("cap_pmos_06v0_b", GF180CapParams),
}

# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()
# Add each to the `modules` namespace
for name, mod in xtors.items():
    setattr(modules, name[0], mod)
for name, mod in ress.items():
    setattr(modules, name, mod)
for name, mod in caps.items():
    setattr(modules, name, mod)
for name, mod in diodes.items():
    setattr(modules, name, mod)
for name, mod in bjts.items():
    setattr(modules, name, mod)


@dataclass
class Cache:
    """# Module-Scope Cache(s)"""

    mos_modcalls: Dict[MosParams, h.ExternalModuleCall] = field(default_factory=dict)

    res_modcalls: Dict[PhysicalResistorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )

    cap_modcalls: Dict[PhysicalCapacitorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )

    diode_modcalls: Dict[DiodeParams, h.ExternalModule] = field(default_factory=dict)

    bjt_modcalls: Dict[BipolarParams, h.ExternalModule] = field(default_factory=dict)


CACHE = Cache()

default_xtor_size = {
    "pfet_03v3": (0.220 * µ, 0.280 * µ),
    "nfet_03v3": (0.220 * µ, 0.280 * µ),
    "nfet_06v0": (0.300 * µ, 0.700 * µ),
    "pfet_06v0": (0.300 * µ, 0.500 * µ),
    "nfet_03v3_dss": (0.220 * µ, 0.280 * µ),
    "pfet_03v3_dss": (0.220 * µ, 0.280 * µ),
    "nfet_06v0_dss": (0.300 * µ, 0.500 * µ),
    "pfet_06v0_dss": (0.300 * µ, 0.500 * µ),
    "nfet_06v0_nvt": (0.800 * µ, 1.800 * µ),
}

default_res_size = {
    "nplus_u": (1 * µ, 1 * µ),
    "pplus_u": (1 * µ, 1 * µ),
    "nplus_s": (1 * µ, 1 * µ),
    "pplus_s": (1 * µ, 1 * µ),
    "nwell": (1 * µ, 1 * µ),
    "npolyf_u": (1 * µ, 1 * µ),
    "ppolyf_u": (1 * µ, 1 * µ),
    "npolyf_s": (1 * µ, 1 * µ),
    "ppolyf_s": (1 * µ, 1 * µ),
    "ppolyf_u_1k": (1 * µ, 1 * µ),
    "ppolyf_u_2k": (1 * µ, 1 * µ),
    "ppolyf_u_1k_6p0": (1 * µ, 1 * µ),
    "ppolyf_u_2k_6p0": (1 * µ, 1 * µ),
    "ppolyf_u_3k": (1 * µ, 1 * µ),
    "rm1": (1 * µ, 1 * µ),
    "rm2": (1 * µ, 1 * µ),
    "rm3": (1 * µ, 1 * µ),
    "tm6k": (1 * µ, 1 * µ),
    "tm9k": (1 * µ, 1 * µ),
    "tm11k": (1 * µ, 1 * µ),
    "tm30k": (1 * µ, 1 * µ),
}

default_diode_size = {
    "diode_nd2ps_03v3": (1 * µ, 1 * µ),
    "diode_pd2nw_03v3": (1 * µ, 1 * µ),
    "diode_nd2ps_06v0": (1 * µ, 1 * µ),
    "diode_pd2nw_06v0": (1 * µ, 1 * µ),
    "diode_nw2ps_03v3": (1 * µ, 1 * µ),
    "diode_nw2ps_06v0": (1 * µ, 1 * µ),
    "diode_pw2dw": (1 * µ, 1 * µ),
    "diode_dw2ps": (1 * µ, 1 * µ),
    "sc_diode": (1 * µ, 1 * µ),
}
