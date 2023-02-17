""" 
# {{cookiecutter.repo_name}} 
## {{cookiecutter.pdk_name}} Hdl21 PDK Package
"""

# Std-Lib Imports
import copy
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from types import SimpleNamespace

# Py
from pydantic.dataclasses import dataclass

import hdl21 as h
from hdl21.prefix import m, MEGA
from hdl21.sim import SimAttr, Lib, Include, Param
from hdl21.pdk import PdkInstallation, Corner, CmosCorner
from hdl21.primitives import (
    Mos,
    MosType,
    MosVth,
    PhysicalResistor,
    PhysicalResistorParams,
)
from hdl21.primitives import MosParams as HDLMosParams


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

    models: Path  # Path to `models.scs`
    parameters: Path  # Path to `parameters.scs`

    def include(self, corner: Corner) -> List[SimAttr]:
        """Return a list of the simulation attributes required to include `corner`."""
        sections = _corner_section_names(corner)
        return (
            # Set the `corner_factor` parameter, which I guess I see why they left external
            [Param(name="corner_factor", val=1)]
            + [Lib(path=self.parameters, section=c) for c in sections]
            + [Include(path=self.models)]
        )


@h.paramclass
class MosParams:
    """Parameters for the PDK MOS transistor modules.
    Defaults correspond to the minimum-sized unit device."""

    w = h.Param(dtype=h.Scalar, desc="Width, in PDK Units (microns)", default=420 * m)
    l = h.Param(dtype=h.Scalar, desc="Length, in PDK Units (microns)", default=150 * m)
    nf = h.Param(dtype=int, desc="Number of Fingers. MAX VALUE IS TWO (2).", default=1)
    m = h.Param(dtype=int, desc="Multiplier", default=1)


def _xtor_module(modname: str) -> h.ExternalModule:
    """Transistor module creator, with module-name `name`."""
    return h.ExternalModule(
        domain="s130",
        name=modname,
        desc=f"S130 PDK Mos {modname}",
        port_list=copy.deepcopy(Mos.port_list),
        paramtype=MosParams,
    )


# # Transistors
#
# Mapping from `MosType` and `MosVth`s to module-names.
#
xtors: Dict[Tuple[MosType, MosVth], h.ExternalModule] = {
    (MosType.NMOS, MosVth.STD): _xtor_module("nmos"),
    (MosType.NMOS, MosVth.LOW): _xtor_module("nmos_lvt"),
    # Note there are no NMOS HVT!
    (MosType.PMOS, MosVth.STD): _xtor_module("pmos"),
    (MosType.PMOS, MosVth.HIGH): _xtor_module("pmos_hvt"),
    # NOTE: PMOS LVT was always in the S130 NDA'ed PDK.
    # It *was not* always in the OSS PDK, but was added at some point.
    # Added here for v3.0.
    (MosType.PMOS, MosVth.LOW): _xtor_module("pmos_lvt"),
}


@h.paramclass
class S130ResParams:
    """Parameters for the Sky130 Resistors"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (Microns)", default=1000 * m)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (Microns)", default=1000 * m)


def _res_module(modname: str) -> h.ExternalModule:
    """Resistor Module creator"""
    return h.ExternalModule(
        domain="s130",
        name=modname,
        desc=f"S130 PDK Res {modname}",
        port_list=copy.deepcopy(PhysicalResistor.port_list),
        paramtype=S130ResParams,
    )


resistors: Dict[str, h.ExternalModule] = {
    "rpoly": _res_module("rpoly"),
    "rpoly_hp": _res_module("rpoly_hp"),
}

# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()
for mod in xtors.values():
    # Add each to the `modules` namespace
    setattr(modules, mod.name, mod)
for mod in resistors.values():
    setattr(modules, mod.name, mod)


@h.paramclass
class IoMosParams:
    """Parameters for the IO transistors.
    Defaults correspond to the minimum-sized unit device.
    Identical to the core transistor `MosParams` except for default values."""

    w = h.Param(dtype=h.Scalar, desc="Width, in PDK Units (microns)", default=420 * m)
    l = h.Param(dtype=h.Scalar, desc="Length, in PDK Units (microns)", default=500 * m)
    nf = h.Param(dtype=int, desc="Number of Fingers. MAX VALUE IS TWO (2).", default=1)
    m = h.Param(dtype=int, desc="Multiplier", default=1)


class IoMosModel(Enum):
    """Enumerated values for the `hdl21.primitives.MosParams.model` field
    which map to the PDK's IO transistors"""

    V5 = "v5"
    NAT_V5 = "nat_v5"
    NAT_V3 = "nat_v3"


io_xtors: Dict[Tuple[MosType, IoMosModel], h.ExternalModule] = dict()

# Add the IO transistors to the `modules` namespace and `io_xtors` dict
io_xtors[(MosType.PMOS, IoMosModel.V5)] = modules.pmos_v5 = h.ExternalModule(
    domain="s130",
    name="pmos_v5",
    desc=f"S130 PDK 5V PMOS (pmos_v5)",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=IoMosParams,
)
io_xtors[(MosType.NMOS, IoMosModel.V5)] = modules.nmos_v5 = h.ExternalModule(
    domain="s130",
    name="nmos_v5",
    desc=f"S130 PDK 5V NMOS (nmos_v5)",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=IoMosParams,
)
io_xtors[(MosType.NMOS, IoMosModel.NAT_V5)] = modules.nmos_nat_v5 = h.ExternalModule(
    domain="s130",
    name="nmos_nat_v5",
    desc=f"S130 PDK Native 5V NMOS (nmos_nat_v5)",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=IoMosParams,
)
io_xtors[(MosType.NMOS, IoMosModel.NAT_V3)] = modules.nmos_nat_v3 = h.ExternalModule(
    domain="s130",
    name="nmos_nat_v3",
    desc=f"S130 PDK Native 3.3V NMOS (nmos_nat_v3)",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=IoMosParams,
)


class MosFamily(Enum):
    """# Mos Transistor "Families"
    The word we use here for distinguishing "core" vs "io"."""

    CORE = "CORE"
    IO = "IO"


class Walker(h.HierarchyWalker):
    """Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s."""

    def __init__(self):
        super().__init__()
        # Caches of our external module calls
        self.mos_modcalls = dict()
        self.res_modcalls = dict()

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.primitive.Mos` with our `ExternalModule`s"""
        # Replace transistors
        if call.prim is h.primitives.Mos:
            return self.mos_module_call(call.params)
        elif call.prim is h.primitives.PhysicalResistor:
            return self.res_module_call(call.params)
        # Return everything else as-is
        return call

    def mos_module_call(self, params: HDLMosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in self.mos_modcalls:
            return self.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        family, mod = self.mos_module(params)

        # Convert to `mod`s parameter-space
        # Note this silly PDK keeps parameter-values in *microns* rather than SI meters.
        w = self.scale_param(params.w, 420 * m)  # FIXME: depend on the default directly
        if family == MosFamily.IO:
            l = self.scale_param(params.l, 500 * m)
            modparams = IoMosParams(w=w, l=l, nf=1, m=params.npar)
        else:
            l = self.scale_param(params.l, 150 * m)
            modparams = MosParams(w=w, l=l, nf=1, m=params.npar)

        # Combine the two into a call, cache and return it
        modcall = mod(modparams)
        self.mos_modcalls[params] = modcall
        return modcall

    def mos_module(self, params: HDLMosParams) -> Tuple[MosFamily, h.ExternalModule]:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        if params.model is not None:
            # A non-default `model` field dictates IO device flavors
            family = MosFamily.IO
            mod = io_xtors.get((params.tp, IoMosModel(params.model)), None)
        else:  # Core transistor, no "model" specified
            family = MosFamily.CORE
            mod = xtors.get((params.tp, params.vth), None)
        if mod is None:
            msg = f"No Mos module for model params `{params}` in family {family}"
            raise RuntimeError(msg)
        return (family, mod)

    def res_module(self, params: PhysicalResistorParams) -> h.ExternalModule:
        mod = resistors.get(params.model, None)
        if mod is None:
            raise RuntimeError(f"No Res module for res model {params.model}")
        return mod

    def res_module_call(self, params: PhysicalResistorParams) -> h.ExternalModuleCall:
        """Retrieve or create  a `Call` for Resistor Parameters `params`."""
        # Check if in Res Cache
        if params in self.res_modcalls:
            return self.res_modcalls[params]

        # Create new ExternalModuleCall based on Resistor Type
        mod = self.res_module(params)

        # Convert to `mod`s parameter-space
        # Defaults from PDK User guide, Width = 1um, L = 1um
        # TODO Do these defaults actually always work?
        w = self.scale_param(params.w, 1000 * m)
        l = self.scale_param(params.l, 1000 * m)
        modparams = S130ResParams(w=w, l=l)

        modcall = mod(modparams)
        self.res_modcalls[params] = modcall
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


def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the S130 technology"""
    Walker.walk(src)
