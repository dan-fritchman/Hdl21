""" 

# Hdl21 + SkyWater 130nm Open-Source PDK Modules and Transformations 

Defines a set of `hdl21.ExternalModule`s comprising the essential devices of the SkyWater 130nm open-source PDK, '
and an `hdl21pdk.netlist` method for converting process-portable `hdl21.Primitive` elements into these modules. 

The complete 130nm design kit includes hundreds of devices. A small subset are targets for conversion from `hdl21.Primitive`. 
They include: 

* "Core" Mos transistors `sky130_fd_pr__{nfet,pfet}_01v8{,_lvt,_hvt}

And may in the near future also include: 

* Resistors `sky130_fd_pr__res_*`
* Capacitors `sky130_fd_pr__cap_*`
* Bipolar Transistors `sky130_fd_pr__{npn,pnp}_*`
* Diodes, which the PDK provides as SPICE `.model` statements alone, and will correspondingly need to be `hdl21.Module`s. 

Many of the latter include a variety of "de-parameterization" steps not yet tested by this package's authors.  

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
from hdl21.prefix import  µ, MILLI, TERA, MEGA
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
PDK_NAME = "sky130"


@h.paramclass
class MosParams:
    """# Sky130 Mos Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=650 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=150 * MILLI)
    nf = h.Param(dtype=h.Scalar, desc="Number of Fingers", default=1)
    mult = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


# FIXME: keep this alias as prior versions may have used it
Sky130MosParams = MosParams


@h.paramclass
class Sky130GenResParams:
    """# Sky130 Generic Resistor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    m = h.Param(dtype=h.Scalar, desc="Multiplicity", default=1)


@h.paramclass
class Sky130PrecResParams:
    """# Sky130 Precision Resistor Parameters"""

    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    mult = h.Param(dtype=h.Scalar, desc="Multiplicity", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplicity", default=1)


@h.paramclass
class Sky130MimParams:
    """# Sky130 MiM Capacitor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    mf = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class Sky130VarParams:
    """# Sky130 Varactor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    vm = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


# FIXME: These params will not autoscale arguments, it doesn't really matter that they don't
# defaults are all that is really valid, but it'd be nice if an error could be thrown with
# parameters being provided or some kind of scaling in the class.
@h.paramclass
class Sky130VPPParams:
    """# Sky130 VPP Capacitor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    mult = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class Sky130DiodeParams:

    # FIXME: What are these junk units supposed to be for?
    a = h.Param(
        dtype=h.Scalar, desc="Area in PDK Units for Diodes (pm²)", default=1 * TERA
    )
    pj = h.Param(
        dtype=h.Scalar,
        desc="Periphery junction capacitance in aF (?)",
        default=4 * MEGA,
    )


@h.paramclass
class Sky130BipolarParams:
    """Default Sky130 Parameters for Bipolar Transistors"""

    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


def _xtor_module(modname: str) -> h.ExternalModule:
    """Transistor module creator, with module-name `name`.
    If optional `MosKey` `key` is provided, adds an entry in the `xtors` dictionary."""

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Mos {modname}",
        port_list=deepcopy(h.Mos.port_list),
        paramtype=MosParams,
    )

    return mod


def _res_module(modname: str, numterminals: int, params=h.Param) -> h.ExternalModule:
    """Resistor Module creator"""

    num2device = {2: PhysicalResistor, 3: ThreeTerminalResistor}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Res{numterminals} {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=params,
    )

    return mod


def _diode_module(modname: str) -> h.ExternalModule:

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Diode {modname}",
        port_list=deepcopy(Diode.port_list),
        paramtype=Sky130DiodeParams,
    )

    return mod


def _bjt_module(modname: str) -> h.ExternalModule:

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK BJT {modname}",
        port_list=deepcopy(Bipolar.port_list),
        paramtype=Sky130BipolarParams,
    )

    return mod


def _cap_module(modname: str, numterminals: int, params: h.Param) -> h.ExternalModule:

    num2device = {2: PhysicalCapacitor, 3: ThreeTerminalCapacitor}

    """Capacitor Module creator"""
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Cap{numterminals} {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=params,
    )

    return mod


PerpVPPPorts = [
    h.Port(name="p"),
    h.Port(name="n"),
    h.Port(name="t", desc="Top Shield"),
    h.Port(name="b", desc="Bottom Shield"),
]


def _vpp_module(modname: str, num_terminals: int) -> h.ExternalModule:
    """VPP Creator module"""

    if num_terminals == 3:

        mod = h.ExternalModule(
            domain=PDK_NAME,
            name=modname,
            desc=f"{PDK_NAME} PDK Parallel VPP {num_terminals} {modname}",
            port_list=deepcopy(h.primitives.ThreeTerminalPorts),
            paramtype=Sky130VPPParams,
        )

    elif num_terminals == 4:

        mod = h.ExternalModule(
            domain=PDK_NAME,
            name=modname,
            desc=f"{PDK_NAME} PDK Perpendicular VPP {modname}",
            port_list=deepcopy(PerpVPPPorts),
            paramtype=Sky130VPPParams,
        )

    return mod


# Individuate component types
MosKey = Tuple[str, MosType, MosVth, MosFamily]

mos_corners: Dict[CmosCorner, str] = {
    CmosCorner.TT: "fet_tt",
    CmosCorner.FF: "fet_ff",
    CmosCorner.SS: "fet_ss",
}
res_corners: Dict[Corner, str] = {
    Corner.TYP: "res_nom",
    Corner.FAST: "res_low",
    Corner.SLOW: "res_high",
}
cap_corners: Dict[Corner, str] = {
    Corner.TYP: "cap_nom",
    Corner.FAST: "cap_low",
    Corner.SLOW: "cap_high",
}


def _corner_section_names(corner: Corner) -> List[str]:
    """Get the include-section names for `corner`."""

    TYP, FAST, SLOW = Corner.TYP, Corner.FAST, Corner.SLOW
    TT, FF, SS = CmosCorner.TT, CmosCorner.FF, CmosCorner.SS

    if corner == Corner.TYP:
        return [mos_corners[TT], res_corners[TYP], cap_corners[TYP]]
    if corner == Corner.FAST:
        return [mos_corners[FF], res_corners[FAST], cap_corners[FAST]]
    if corner == Corner.SLOW:
        return [mos_corners[SS], res_corners[SLOW], cap_corners[SLOW]]

    raise ValueError(f"Invalid corner: {corner}")


@dataclass
class Install(PdkInstallation):
    """Pdk Installation Data
    External data provided by site-specific installations"""

    model_lib: Path  # Path to the transistor models included in this module

    def include(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner`."""

        mos_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in mos_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=mos_corners[corner])


xtors: Dict[MosKey, h.ExternalModule] = {
    # Add all generic transistors
    ("NMOS_1p8V_STD", MosType.NMOS, MosVth.STD, MosFamily.CORE): _xtor_module("sky130_fd_pr__nfet_01v8"),
    ("NMOS_1p8V_LOW", MosType.NMOS, MosVth.LOW, MosFamily.CORE): _xtor_module("sky130_fd_pr__nfet_01v8_lvt"),
    ("PMOS_1p8V_STD", MosType.PMOS, MosVth.STD, MosFamily.CORE): _xtor_module("sky130_fd_pr__pfet_01v8"),
    ("PMOS_1p8V_HIGH", MosType.PMOS, MosVth.HIGH, MosFamily.CORE): _xtor_module("sky130_fd_pr__pfet_01v8_hvt"),
    ("PMOS_1p8V_LOW", MosType.PMOS, MosVth.LOW, MosFamily.CORE): _xtor_module("sky130_fd_pr__pfet_01v8_lvt"),
    ("PMOS_5p5V_D10_STD", MosType.PMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__pfet_g5v0d10v5"
    ),
    ("NMOS_5p5V_D10_STD", MosType.NMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__nfet_g5v0d10v5"
    ),
    ("PMOS_5p5V_D16_STD", MosType.PMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__pfet_g5v0d16v0"
    ),
    ("NMOS_20p0V_STD", MosType.NMOS, MosVth.STD, MosFamily.NONE): _xtor_module("sky130_fd_pr__nfet_20v0"),
    ("NMOS_20p0V_LOW", MosType.NMOS, MosVth.ZERO, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0_zvt"
    ),
    ("NMOS_ISO_20p0V", MosType.NMOS, MosVth.STD, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0_iso"
    ),
    ("PMOS_20p0V", MosType.PMOS, MosVth.STD, MosFamily.NONE): _xtor_module("sky130_fd_pr__pfet_20v0"),
    # Note there are no NMOS HVT!
    # Add Native FET entries
    ("NMOS_3p3V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): _xtor_module("sky130_fd_pr__nfet_03v3_nvt"),
    ("NMOS_5p0V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): _xtor_module("sky130_fd_pr__nfet_05v0_nvt"),
    ("NMOS_20p0V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0_nvt"
    ),
    # Add ESD FET entries
    ("ESD_NMOS_1p8V", MosType.NMOS, MosVth.STD, MosFamily.CORE): _xtor_module("sky130_fd_pr__esd_nfet_01v8"),
    ("ESD_NMOS_5p5V_D10", MosType.NMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__esd_nfet_g5v0d10v5"
    ),
    ("ESD_NMOS_5p5V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__esd_nfet_g5v0d10v5_nvt"
    ),
    ("ESD_PMOS_5p5V", MosType.PMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__esd_pfet_g5v0d10v5"
    ),
}

ress: Dict[str, h.ExternalModule] = {
    # 2-terminal generic resistors
    "GEN_PO": _res_module("sky130_fd_pr__res_generic_po", 2, Sky130GenResParams),
    "GEN_LI": _res_module("sky130_fd_pr__res_generic_l1", 2, Sky130GenResParams),
    "GEN_M1": _res_module("sky130_fd_pr__res_generic_m1", 2, Sky130GenResParams),
    "GEN_M2": _res_module("sky130_fd_pr__res_generic_m2", 2, Sky130GenResParams),
    "GEN_M3": _res_module("sky130_fd_pr__res_generic_m3", 2, Sky130GenResParams),
    "GEN_M4": _res_module("sky130_fd_pr__res_generic_m4", 2, Sky130GenResParams),
    "GEN_M5": _res_module("sky130_fd_pr__res_generic_m5", 2, Sky130GenResParams),
    # 3-terminal generic resistors
    "GEN_ND": _res_module("sky130_fd_pr__res_generic_nd", 3, Sky130GenResParams),
    "GEN_PD": _res_module("sky130_fd_pr__res_generic_pd", 3, Sky130GenResParams),
    "GEN_ISO_PW": _res_module("sky130_fd_pr__res_iso_pw", 3, Sky130GenResParams),
    # 3-terminal precision resistors
    "PP_PREC_0p35": _res_module(
        "sky130_fd_pr__res_high_po_0p35", 3, Sky130PrecResParams
    ),
    "PP_PREC_0p69": _res_module(
        "sky130_fd_pr__res_high_po_0p69", 3, Sky130PrecResParams
    ),
    "PP_PREC_1p41": _res_module(
        "sky130_fd_pr__res_high_po_1p41", 3, Sky130PrecResParams
    ),
    "PP_PREC_2p85": _res_module(
        "sky130_fd_pr__res_high_po_2p85", 3, Sky130PrecResParams
    ),
    "PP_PREC_5p30": _res_module(
        "sky130_fd_pr__res_high_po_5p3", 3, Sky130PrecResParams
    ),
    "PM_PREC_0p35": _res_module(
        "sky130_fd_pr__res_xhigh_po_0p35", 3, Sky130PrecResParams
    ),
    "PM_PREC_0p69": _res_module(
        "sky130_fd_pr__res_xhigh_po_0p69", 3, Sky130PrecResParams
    ),
    "PM_PREC_1p41": _res_module(
        "sky130_fd_pr__res_xhigh_po_1p41", 3, Sky130PrecResParams
    ),
    "PM_PREC_2p85": _res_module(
        "sky130_fd_pr__res_xhigh_po_2p85", 3, Sky130PrecResParams
    ),
    "PM_PREC_5p30": _res_module(
        "sky130_fd_pr__res_xhigh_po_5p3", 3, Sky130PrecResParams
    ),
}

diodes: Dict[str, h.ExternalModule] = {
    # Add diodes
    "PWND_5p5V": _diode_module("sky130_fd_pr__diode_pw2nd_05v5"),
    "PWND_11p0V": _diode_module("sky130_fd_pr__diode_pw2nd_11v0"),
    "PWND_5p5V_NAT": _diode_module("sky130_fd_pr__diode_pw2nd_05v5_nvt"),
    "PWND_5p5V_LVT": _diode_module("sky130_fd_pr__diode_pw2nd_05v5_lvt"),
    "PDNW_5p5V": _diode_module("sky130_fd_pr__diode_pd2nw_05v5"),
    "PDNW_11p0V": _diode_module("sky130_fd_pr__diode_pd2nw_11v0"),
    "PDNW_5p5V_HVT": _diode_module("sky130_fd_pr__diode_pd2nw_05v5_hvt"),
    "PDNW_5p5V_LVT": _diode_module("sky130_fd_pr__diode_pd2nw_05v5_lvt"),
    "PX_RF_PSNW": _diode_module("sky130_fd_pr__model__parasitic__rf_diode_ps2nw"),
    "PX_RF_PWDN": _diode_module("sky130_fd_pr__model__parasitic__rf_diode_pw2dn"),
    "PX_PWDN": _diode_module("sky130_fd_pr__model__parasitic__diode_pw2dn"),
    "PX_PSDN": _diode_module("sky130_fd_pr__model__parasitic__diode_ps2dn"),
    "PX_PSNW": _diode_module("sky130_fd_pr__model__parasitic__diode_ps2nw"),
}

bjts: Dict[str, h.ExternalModule] = {
    # Add BJTs
    "NPN_5p0V" : _bjt_module("sky130_fd_pr__npn_05v5"),
    "NPN_11p0V" : _bjt_module("sky130_fd_pr__npn_11v0"),
    "PNP_5p0V" : _bjt_module("sky130_fd_pr__pnp_05v5"),
}

caps: Dict[str, h.ExternalModule] = {
    # List all MiM capacitors
    "MIM_M3": _cap_module("sky130_fd_pr__cap_mim_m3__base", 2, Sky130MimParams),
    "MIM_M4": _cap_module("sky130_fd_pr__cap_mim_m4__base", 2, Sky130MimParams),
    # List available Varactors
    "VAR_LVT": _cap_module("sky130_fd_pr__cap_var_lvt", 3, Sky130VarParams),
    "VAR_HVT": _cap_module("sky130_fd_pr__cap_var_hvt", 3, Sky130VarParams),
}

vpps: Dict[str, h.ExternalModule] = {
    # List Parallel VPP capacitors
    "VPP_PARA_1": _vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2", 3),
    "VPP_PARA_2": _vpp_module("sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield", 3),
    "VPP_PARA_3": _vpp_module("sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_noshield", 3),
    "VPP_PARA_4": _vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield", 3),
    "VPP_PARA_5": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_noshield", 3),
    "VPP_PARA_6": _vpp_module("sky130_fd_pr__cap_vpp_44p7x23p1_pol1m1m2m3m4m5_noshield", 3),
    "VPP_PARA_7": _vpp_module("sky130_fd_pr__cap_vpp_02p7x06p1_m1m2m3m4_shieldl1_fingercap",3),
    "VPP_PARA_8": _vpp_module("sky130_fd_pr__cap_vpp_02p9x06p1_m1m2m3m4_shieldl1_fingercap2",3),
    "VPP_PARA_9": _vpp_module("sky130_fd_pr__cap_vpp_02p7x11p1_m1m2m3m4_shieldl1_fingercap",3),
    "VPP_PARA_10": _vpp_module("sky130_fd_pr__cap_vpp_02p7x21p1_m1m2m3m4_shieldl1_fingercap",3),
    "VPP_PARA_11": _vpp_module("sky130_fd_pr__cap_vpp_02p7x41p1_m1m2m3m4_shieldl1_fingercap",3),
    # List Perpendicular VPP capacitors
    "VPP_PERP_1": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5", 4),
    "VPP_PERP_2": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5", 4),
    "VPP_PERP_3": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3m4_shieldl1m5", 4),
    "VPP_PERP_4": _vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1m5_floatm4",4),
    "VPP_PERP_5": _vpp_module("sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1m5_floatm4",4),
    "VPP_PERP_6": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1m5_floatm4",4),
    "VPP_PERP_7": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3_shieldm4", 4),
    "VPP_PERP_8": _vpp_module("sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2m3_shieldpom4", 4),
    "VPP_PERP_9": _vpp_module("sky130_fd_pr__cap_vpp_06p8x06p1_m1m2m3_shieldl1m4", 4),
    "VPP_PERP_10": _vpp_module("sky130_fd_pr__cap_vpp_11p3x11p8_l1m1m2m3m4_shieldm5", 4),
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
for name, mod in vpps.items():
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

# Default param dicts
default_xtor_size = {
    "sky130_fd_pr__nfet_01v8": (h.Scalar(inner=0.420 * µ), h.Scalar(inner=0.150 * µ)),
    "sky130_fd_pr__nfet_01v8_lvt": (h.Scalar(inner=0.420 * µ), h.Scalar(inner=0.150 * µ)),
    "sky130_fd_pr__pfet_01v8": (h.Scalar(inner=0.550 * µ), h.Scalar(inner=0.150 * µ)),
    "sky130_fd_pr__pfet_01v8_hvt": (h.Scalar(inner=0.550 * µ), h.Scalar(inner=0.150 * µ)),
    "sky130_fd_pr__pfet_01v8_lvt": (h.Scalar(inner=0.550 * µ), h.Scalar(inner=0.350 * µ)),
    "sky130_fd_pr__pfet_g5v0d10v5": (h.Scalar(inner=0.420 * µ), h.Scalar(inner=0.500 * µ)),
    "sky130_fd_pr__nfet_g5v0d10v5": (h.Scalar(inner=0.420 * µ), h.Scalar(inner=0.500 * µ)),
    "sky130_fd_pr__pfet_g5v0d16v0": (h.Scalar(inner=5.000 * µ), h.Scalar(inner=0.660 * µ)),
    "sky130_fd_pr__nfet_20v0": (h.Scalar(inner=29.410 * µ), h.Scalar(inner=2.950 * µ)),
    "sky130_fd_pr__nfet_20v0_zvt": (h.Scalar(inner=30.000 * µ), h.Scalar(inner=1.500 * µ)),
    "sky130_fd_pr__nfet_20v0_iso": (h.Scalar(inner=30.000 * µ), h.Scalar(inner=1.500 * µ)),
    "sky130_fd_pr__pfet_20v0": (h.Scalar(inner=30.000 * µ), h.Scalar(inner=1.000 * µ)),
    "sky130_fd_pr__nfet_03v3_nvt": (h.Scalar(inner=0.700 * µ), h.Scalar(inner=0.500 * µ)),
    "sky130_fd_pr__nfet_05v0_nvt": (h.Scalar(inner=0.700 * µ), h.Scalar(inner=0.900 * µ)),
    "sky130_fd_pr__nfet_20v0_nvt": (h.Scalar(inner=30.000 * µ), h.Scalar(inner=1.000 * µ)),
    "sky130_fd_pr__esd_nfet_01v8": (h.Scalar(inner=20.350 * µ), h.Scalar(inner=0.165 * µ)),
    "sky130_fd_pr__esd_nfet_g5v0d10v5": (h.Scalar(inner=14.500 * µ), h.Scalar(inner=0.550 * µ)),
    "sky130_fd_pr__esd_nfet_g5v0d10v5_nvt": (
        h.Scalar(inner=10.000 * µ),
        h.Scalar(inner=0.900 * µ),
    ),
    "sky130_fd_pr__esd_pfet_g5v0d10v5": (h.Scalar(inner=14.500 * µ), h.Scalar(inner=0.550 * µ)),
}

default_gen_res_size = {
    "sky130_fd_pr__res_generic_po": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_l1": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_m1": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_m2": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_m3": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_m4": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_m5": (h.Scalar(inner=0.720 * µ), h.Scalar(inner=0.290 * µ)),
    "sky130_fd_pr__res_generic_nd": (h.Scalar(inner=0.150 * µ), h.Scalar(inner=0.270 * µ)),
    "sky130_fd_pr__res_generic_pd": (h.Scalar(inner=0.150 * µ), h.Scalar(inner=0.270 * µ)),
    # FIXME: This value is lifted from xschem but can't be found in documentation
    "sky130_fd_pr__res_iso_pw": (h.Scalar(inner=2.650 * µ), h.Scalar(inner=2.650 * µ)),
}

"These have to be left in microns for parsing reasons"
default_prec_res_L = {
    "sky130_fd_pr__res_high_po_0p35": h.Scalar(inner=0.350),
    "sky130_fd_pr__res_high_po_0p69": h.Scalar(inner=0.690),
    "sky130_fd_pr__res_high_po_1p41": h.Scalar(inner=1.410),
    "sky130_fd_pr__res_high_po_2p85": h.Scalar(inner=2.850),
    "sky130_fd_pr__res_high_po_5p3": h.Scalar(inner=5.300),
    "sky130_fd_pr__res_xhigh_po_0p35": h.Scalar(inner=0.350),
    "sky130_fd_pr__res_xhigh_po_0p69": h.Scalar(inner=0.690),
    "sky130_fd_pr__res_xhigh_po_1p41": h.Scalar(inner=1.410),
    "sky130_fd_pr__res_xhigh_po_2p85": h.Scalar(inner=2.850),
    "sky130_fd_pr__res_xhigh_po_5p3": h.Scalar(inner=5.300),
}

default_cap_sizes = {
    # FIXME: Using documentation minimum sizing not sure of correct answer
    "sky130_fd_pr__cap_mim_m3__base": (h.Scalar(inner=2.000 * µ), h.Scalar(inner=2.000 * µ)),
    "sky130_fd_pr__cap_mim_m4__base": (h.Scalar(inner=2.000 * µ), h.Scalar(inner=2.000 * µ)),
    "sky130_fd_pr__cap_var_lvt": (h.Scalar(inner=0.180 * µ), h.Scalar(inner=0.180 * µ)),
    "sky130_fd_pr__cap_var_hvt": (h.Scalar(inner=0.180 * µ), h.Scalar(inner=0.180 * µ)),
}


class Sky130Walker(h.HierarchyWalker):
    """Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s."""

    def __init__(self):
        super().__init__()
        # Caches of our external module calls
        self.mos_modcalls = dict()
        self.res_modcalls = dict()
        self.cap_modcalls = dict()
        self.diode_modcalls = dict()
        self.bjt_modcalls = dict()

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.primitive.Mos` with our `ExternalModule`s"""
        # Replace transistors
        if call.prim is Mos:
            return self.mos_module_call(call.params)

        elif call.prim is PhysicalResistor or call.prim is ThreeTerminalResistor:
            return self.res_module_call(call.params)

        elif call.prim is PhysicalCapacitor or call.prim is ThreeTerminalCapacitor:
            return self.cap_module_call(call.params)

        elif call.prim is Diode:
            return self.diode_module_call(call.params)

        elif call.prim is Bipolar:
            return self.bjt_module_call(call.params)

        else:
            raise RuntimeError(f"{call.prim} is not legitimate primitive")

        # Return everything else as-is
        return call

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        if params.model is not None:

            try:
                return [v for k, v in xtors.items() if params.model in k][0]
            except IndexError:
                msg = f"No Mos module for model name {(params.model)}"
                raise RuntimeError(msg)
            
        """
        Here we wittle down our list of potential candidates

        General parameters we're concerned with are:

        1) h.MosType - Most important decision is it a PMOS or an NMOS, default = NMOS
        2) h.MosFamily - Detemines what class of transistor, CORE, IO, HVT, default = CORE
        3) h.MosVth - Mos Threshold, HIGH, STD, LOW, ULTRA_LOW, default = STD
        """

        # Map none to default, otherwise leave alone
        mostype = h.MosType.NMOS if params.tp is None else params.tp
        mosfam = h.MosFamily.CORE if params.family is None else params.family
        mosvth = h.MosVth.STD if params.vth is None else params.vth
        args = (mostype,mosfam,mosvth)

        # Filter the xtors by a dictionary by partial match
        subset = {key: value for key, value in xtors.items() if any(a in key for a in args)}

        # More than one answer? You weren't specific enough.
        if len(subset) != 1:
            msg = f"Mos module choice not well-defined given parameters {args}"
            raise RuntimeError(msg)

        return subset.values()[0]

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in CACHE.mos_modcalls:
            return CACHE.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        w, l = self.use_defaults(params, mod.name, default_xtor_size)

        modparams = Sky130MosParams(
            w=w,
            l=l,
            nf=params.npar,  # FIXME: renaming
            mult=params.mult,
        )

        # Combine the two into a call, cache and return it
        modcall = mod(modparams)
        CACHE.mos_modcalls[params] = modcall
        return modcall

    def res_module(self, params: PhysicalResistorParams):
        """Retrieve or create an `ExternalModule` for a Resistor of parameters `params`."""
        mod = ress.get((params.model), None)

        if mod is None:
            msg = f"No Res module for model {params.model}"
            raise RuntimeError(msg)

        return mod

    def res_module_call(self, params: PhysicalResistorParams):

        # First check our cache
        if params in CACHE.res_modcalls:
            return CACHE.res_modcalls[params]

        mod = self.res_module(params)

        if mod.paramtype == Sky130GenResParams:

            w, l = self.use_defaults(params, mod.name, default_gen_res_size)

            modparams = Sky130GenResParams(w=w, l=l)

        elif mod.paramtype == Sky130PrecResParams:

            l = default_prec_res_L[mod.name]

            modparams = Sky130PrecResParams(l=l)

        modcall = mod(modparams)
        CACHE.res_modcalls[params] = modcall
        return modcall

    def cap_module(self, params: Any):
        """Retrieve or create an `ExternalModule` for a Capacitor of parameters `params`."""
        mod = caps.get((params.model), None)

        if mod is None:
            msg = f"No Capacitor module for model {params.model}"
            raise RuntimeError(msg)

        return mod

    def cap_module_call(self, params: PhysicalCapacitorParams):

        if params in CACHE.cap_modcalls:
            return CACHE.cap_modcalls[params]

        mod = self.cap_module(params)

        m = 1

        if params.mult is not None:

            m = int(params.mult)

        if mod.paramtype == Sky130MimParams:

            w, l = self.use_defaults(params, mod.name, default_cap_sizes)
            modparams = Sky130MimParams(w=w, l=l, mf=m)

        elif mod.paramtype == Sky130VarParams:

            w, l = self.use_defaults(params, mod.name, default_cap_sizes)
            modparams = Sky130VarParams(w=w, l=l, vm=m)

        modcall = mod(modparams)
        CACHE.cap_modcalls[params] = modcall
        return modcall

    def diode_module(self, params: DiodeParams):
        """Retrieve or create an `ExternalModule` for a Diode of parameters `params`."""
        mod = diodes.get((params.model), None)
            
        if mod is None:
            msg = f"No Diode module for model {params.model}"
            raise RuntimeError(msg)

        return mod

    def diode_module_call(self, params: DiodeParams):

        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.diode_module(params)

        if params.w is not None and params.w is not None:

            # This scaling is a quirk of SKY130
            a = params.w * params.l * 1 * TERA
            pj = 2 * (params.w + params.l) * MEGA
            modparams = Sky130DiodeParams(a=a,pj=pj)

        else:

            modparams = Sky130DiodeParams()

        modcall = mod(modparams)
        CACHE.diode_modcalls[params] = modcall
        return modcall

    def bjt_module(self, params: BipolarParams):
        """Retrieve or create an `ExternalModule` for a Bipolar of parameters `params`."""
        mod = bjts.get(params.model, None)

        if mod is None:
            msg = f"No Bipolar module for model {params.mparamsodel}"
            raise RuntimeError(msg)

        return mod

    def bjt_module_call(self, params: BipolarParams):

        if params in CACHE.bjt_modcalls:
            return CACHE.bjt_modcalls[params]

        mod = self.bjt_module(params)

        if params.mult is not None:
            mult = int(params.mult)
        else:
            mult = 1

        modparams = Sky130BipolarParams(m=mult)

        modcall = mod(modparams)
        CACHE.bjt_modcalls[params] = modcall
        return modcall

    def scale_param(self, orig: Optional[h.Scalar], default: h.Prefixed) -> h.Scalar:
        """Replace device size parameter-value `orig`.
        Primarily type-dispatches across the need to scale to microns for this PDK."""
        if orig is None:
            return default
        if not isinstance(orig, h.Scalar):
            raise TypeError(f"Invalid Scalar parameter {orig}")
        inner = orig.inner
        if isinstance(inner, h.Prefixed):
            return h.Scalar(inner=inner * MEGA)
        if isinstance(inner, h.Literal):
            return h.Scalar(inner=h.Literal(f"({inner} * 1e6)"))
        raise TypeError(f"Param Value {inner}")

    def use_defaults(self, params: h.paramclass, modname: str, defaults: dict):

        w, l = None, None

        if params.w is None:

            w = defaults[modname][0]

        else:

            w = params.w

        if params.l is None:

            l = defaults[modname][1]

        else:

            l = params.l

        w = self.scale_param(w, 1000 * MILLI)
        l = self.scale_param(l, 1000 * MILLI)

        return w, l

def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the Sample technology"""
    Sky130Walker().walk(src)
