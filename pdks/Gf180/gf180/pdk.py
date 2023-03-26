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

# Introduce an empty paramclass for predetermined cells
GF180DeviceParams = h.HasNoParams


@h.paramclass
class MosParams:
    """# GF180 Mos Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1 * µ)
    nf = h.Param(dtype=h.Scalar, desc="Number of Fingers", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)

# FIXME: keep this alias as prior versions may have used it
GF180MosParams = MosParams

@h.paramclass
class GF180ResParams:
    """# GF180 Generic Resistor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (m)", default=1 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (m)", default=1 * µ)
    m = h.Param(dtype=h.Scalar, desc="Length in PDK Units (m)", default=1)

@h.paramclass
class GF180CapParams:
    """# GF180 Capacitor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (m)", default=1 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (m)", default=1 * µ)
    m = h.Param(dtype=h.Scalar, desc="Parallel Multiplier", default=1)

@h.paramclass
class GF180DiodeParams:
    """# GF180 Diode Parameters"""

    area = h.Param(dtype=h.Scalar, desc="Area in PDK Units (m²)", default=1 * p)
    pj = h.Param(dtype=h.Scalar, desc="Junction Perimeter in PDK units (m)", default=4 * µ)

@h.paramclass
class GF180BipolarParams:
    """# GF180 Bipolar Parameters"""

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

FourTerminalBipolarPorts = [
    h.Port(name="c"),
    h.Port(name="b"),
    h.Port(name="e"),
    h.Port(name="s"),
]

def _bjt_module(modname: str, num_terminals = 3) -> h.ExternalModule:

    num2device = {3:Bipolar.port_list, 4:FourTerminalBipolarPorts}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK {num_terminals}-terminal BJT {modname}",
        port_list=deepcopy(num2device[num_terminals]),
        paramtype=GF180BipolarParams,
    )

    return mod


@dataclass
class Install(PdkInstallation):
    """Pdk Installation Data
    External data provided by site-specific installations"""

    model_lib: Path  # Path to the transistor models included in this module

    def include_design(self) -> h.sim.Include:

        return h.sim.Include(path=self.model_lib.parent/"design.ngspice")

    def include_mos(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for MOSFETs"""

        mos_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "typical",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        return h.sim.Lib(path=self.model_lib, section=mos_corners[corner])

    def include_resistors(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for Resistors"""

        res_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "res_typical",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in res_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=res_corners[corner])

    def include_diodes(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for Diodes"""

        diode_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "diode_typical",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in diode_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=diode_corners[corner])

    def include_bjts(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for BJTs"""

        bjt_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "bjt_typical",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in bjt_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=bjt_corners[corner])

    def include_moscaps(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for MOS Capacitors"""

        moscap_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "moscap_typical",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in moscap_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=moscap_corners[corner])

    def include_mimcaps(self, corner: h.pdk.Corner) -> h.sim.Lib:

        mimcap_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "mimcap_typical",
            h.pdk.Corner.FAST: FIXME,
            h.pdk.Corner.SLOW: FIXME,
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in mimcap_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=mimcap_corners[corner])


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
    "NPN_10p0x10p0": _bjt_module("npn_10p00x10p00",4),
    "NPN_5p0x5p0": _bjt_module("npn_05p00x05p00",4),
    "NPN_0p54x16p0": _bjt_module("npn_00p54x16p00",4),
    "NPN_0p54x8p0": _bjt_module("npn_00p54x08p00",4),
    "NPN_0p54x4p0": _bjt_module("npn_00p54x04p00",4),
    "NPN_0p54x2p0": _bjt_module("npn_00p54x02p00",4),
}

caps: Dict[str, h.ExternalModule] = {
    "MIM_1p5fF": _cap_module("cap_mim_1f5fF", 2, GF180CapParams),
    "MIM_1p0fF": _cap_module("cap_mim_1f0fF", 2, GF180CapParams),
    "MIM_2p0fF": _cap_module("cap_mim_2f0fF", 2, GF180CapParams),
    "NMOS_3p3V": _cap_module("cap_nmos_03v3", 3, GF180CapParams),
    "PMOS_3p3V": _cap_module("cap_pmos_03v3", 3, GF180CapParams),
    "NMOS_6p0V": _cap_module("cap_nmos_06v0", 3, GF180CapParams),
    "PMOS_6p0V": _cap_module("cap_pmos_06v0", 3, GF180CapParams),
    "NMOS_Nwell_3p3V": _cap_module("cap_nmos_03v3_b", 3, GF180CapParams),
    "PMOS_Pwell_3p3V": _cap_module("cap_pmos_03v3_b", 3, GF180CapParams),
    "NMOS_Nwell_6p0V": _cap_module("cap_nmos_06v0_b", 3, GF180CapParams),
    "PMOS_Pwell_6p0V": _cap_module("cap_pmos_06v0_b", 3, GF180CapParams),
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
    "pfet_03v3" : (h.Scalar(inner=0.220 * µ),h.Scalar(inner=0.280 * µ)),
    "nfet_03v3" : (h.Scalar(inner=0.220 * µ),h.Scalar(inner=0.280 * µ)),
    "nfet_06v0" : (h.Scalar(inner=0.300 * µ),h.Scalar(inner=0.500 * µ)),
    "pfet_06v0" : (h.Scalar(inner=0.300 * µ),h.Scalar(inner=0.500 * µ)),
    "nfet_03v3_dss" : (h.Scalar(inner=0.220 * µ),h.Scalar(inner=0.280 * µ)),
    "pfet_03v3_dss" : (h.Scalar(inner=0.220 * µ),h.Scalar(inner=0.280 * µ)),
    "nfet_06v0_dss" : (h.Scalar(inner=0.300 * µ),h.Scalar(inner=0.500 * µ)),
    "pfet_06v0_dss" : (h.Scalar(inner=0.300 * µ),h.Scalar(inner=0.500 * µ)),
    "nfet_06v0_nvt" : (h.Scalar(inner=0.800 * µ),h.Scalar(inner=1.800 * µ)),
}

default_res_size = {
    "nplus_u" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "pplus_u" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "nplus_s" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "pplus_s" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "nwell" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "npolyf_u" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_u" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "npolyf_s" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_s" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_u_1k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_u_2k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_u_1k_6p0" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_u_2k_6p0" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "ppolyf_u_3k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "rm1" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "rm2" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "rm3" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "tm6k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "tm9k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "tm11k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "tm30k" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
}

default_diode_size = {
    "diode_nd2ps_03v3" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_pd2nw_03v3" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_nd2ps_06v0" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_pd2nw_06v0" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_nw2ps_03v3" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_nw2ps_06v0" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_pw2dw" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "diode_dw2ps" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
    "sc_diode" : (h.Scalar(inner=1*µ), h.Scalar(inner=1*µ)),
}

class Gf180Walker(h.HierarchyWalker):
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

        return call

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        if params.model is not None:
            
            try:
                return [v for k, v in xtors.items() if params.model in k][0]
            except IndexError:
                msg = f"No Mos module for model name {(params.model)}"
                raise RuntimeError(msg)
            
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

        # Convert to `mod`s parameter-space
        w, l = self.use_defaults(params, mod.name, default_xtor_size)

        modparams = GF180MosParams(
            w=w,
            l=l,
            nf=params.npar,  # FIXME: renaming
            m=params.mult,
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

        w,l = self.use_defaults(params, mod.name, default_res_size)

        modparams = GF180ResParams(w=w, l=l)

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

        # First check our cache
        if params in CACHE.cap_modcalls:
            return CACHE.cap_modcalls[params]

        mod = self.cap_module(params)

        w = self.scale_param(params.w, 1000 * MILLI)
        l = self.scale_param(params.l, 1000 * MILLI)

        modparams = GF180CapParams(w=w, l=l)

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

        # First check our cache
        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.diode_module(params)

        w,l = self.use_defaults(params,mod.name,default_diode_size)

        modparams = GF180DiodeParams(area=w*l, pj=2*w+2*l)

        modcall = mod(modparams)
        CACHE.diode_modcalls[params] = modcall
        return modcall

    def bjt_module(self, params: BipolarParams):
        """Retrieve or create an `ExternalModule` for a Bipolar of parameters `params`."""
        mod = bjts.get(params.model, None)

        if mod is None:
            msg = f"No Bipolar module for model combination {(params.model, params.tp)}"
            raise RuntimeError(msg)

        return mod

    def bjt_module_call(self, params: BipolarParams):

        # First check our cache
        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.bjt_module(params)

        modparams = GF180BipolarParams(m = params.mult)

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
            return h.Scalar(inner=inner)
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

        return w, l


def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the Sample technology"""
    Gf180Walker().walk(src)
