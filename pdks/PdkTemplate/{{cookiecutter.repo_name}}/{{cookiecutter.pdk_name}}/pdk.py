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
from dataclasses import field

# PyPi Imports
from pydantic.v1.dataclasses import dataclass

# Hdl21 Imports
import hdl21 as h

PDK_NAME = "{{cookiecutter.pdk_name}}"
FIXME = None  # FIXME: Replace with real values!

# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()


@dataclass
class Install(h.pdk.PdkInstallation):
    """# Pdk Installation Data
    External data provided by site-specific installations"""

    ...  # Empty template, with some suggestions

    # models: Path # Path to the models file

    # def include(self, corner: h.Corner) -> hs.Include:
    #     """Return an `Include` for `corner`."""
    #     ...


@h.paramclass
class MosParams:
    """# {{cookiecutter.pdk_name}} Mos Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width", default=FIXME)
    l = h.Param(dtype=h.Scalar, desc="Length", default=FIXME)
    nf = h.Param(dtype=int, desc="Number of Fingers", default=1)
    mult = h.Param(dtype=int, desc="Multiplier", default=1)


def _xtor_module(modname: str) -> h.ExternalModule:
    """Transistor module creator, with module-name `name`."""
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{{cookiecutter.pdk_name}} PDK Mos {modname}",
        port_list=copy.deepcopy(h.Mos.port_list),
        paramtype=MosParams,
    )
    setattr(modules, modname, mod)
    return mod


# # Transistors
#
# Mapping from `h.MosType` and `MosVth`s to module-names.
#
xtors: Dict[Tuple[h.MosType, h.MosVth], h.ExternalModule] = {
    (h.MosType.NMOS, h.MosVth.STD): _xtor_module("nmos_std"),
    (h.MosType.NMOS, h.MosVth.LOW): _xtor_module("nmos_low"),
    (h.MosType.NMOS, h.MosVth.HIGH): _xtor_module("nmos_high"),
    (h.MosType.PMOS, h.MosVth.STD): _xtor_module("pmos_std"),
    (h.MosType.PMOS, h.MosVth.LOW): _xtor_module("pmos_low"),
    (h.MosType.PMOS, h.MosVth.HIGH): _xtor_module("pmos_high"),
}


@h.paramclass
class ResParams:
    """# {{cookiecutter.pdk_name}} Resistor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units", default=FIXME)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units", default=FIXME)


def _res_module(modname: str) -> h.ExternalModule:
    """Resistor Module creator"""
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Resistor {modname}",
        port_list=copy.deepcopy(h.PhysicalResistor.port_list),
        paramtype=ResParams,
    )
    setattr(modules, modname, mod)
    return mod


resistors: Dict[str, h.ExternalModule] = {
    "rpoly": _res_module("rpoly"),
    "rpoly_hp": _res_module("rpoly_hp"),
}


@dataclass
class Cache:
    """# Module-Scope Cache(s)"""

    mos_modcalls: Dict[h.primitives.Mos.Params, h.ExternalModuleCall] = field(
        default_factory=dict
    )
    res_modcalls: Dict[
        h.primitives.PhysicalResistor.Params, h.ExternalModuleCall
    ] = field(default_factory=dict)


CACHE = Cache()


class Walker(h.HierarchyWalker):
    """# Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s."""

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.primitive.Mos` with our `ExternalModule`s"""
        if call.prim is h.primitives.Mos:  # Replace transistors
            return self.mos_module_call(call.params)
        elif call.prim is h.primitives.PhysicalResistor:  # Replace physical resistors
            return self.res_module_call(call.params)
        return call  # Return everything else as-is

    def mos_module_call(self, params: h.Mos.Params) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in CACHE.mos_modcalls:
            return CACHE.mos_modcalls[params]

        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        # Convert into the PDK's parameter-space
        modparams = self.mos_params(params)

        # Combine the two into a call, cache and return it
        mc = CACHE.mos_modcalls[params] = mod(modparams)
        return mc

    def mos_module(self, params: h.Mos.Params) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""

        mod = xtors.get((params.tp, params.vth), None)
        if mod is None:
            msg = f"No Mos module for model params `{params}`"
            raise RuntimeError(msg)
        return mod

    def mos_params(self, params: h.Mos.Params) -> MosParams:
        """Convert generic `h.Mos.Params` to PDK `MosParams`."""
        raise NotImplementedError  # FIXME!

    def res_module_call(
        self, params: h.primitives.PhysicalResistor.Params
    ) -> h.ExternalModuleCall:
        """Retrieve or create  a `Call` for Resistor Parameters `params`."""
        # First check our cache
        if params in CACHE.res_modcalls:
            return CACHE.res_modcalls[params]

        # Create new ExternalModuleCall based on Resistor Type
        mod = self.res_module(params)

        # Convert into the PDK's parameter-space
        modparams = self.res_params(params)

        # Combine the two into a call, cache and return it
        mc = CACHE.res_modcalls[params] = mod(modparams)
        return mc

    def res_module(
        self, params: h.primitives.PhysicalResistor.Params
    ) -> h.ExternalModule:
        mod = resistors.get(params.model, None)
        if mod is None:
            raise RuntimeError(f"No Res module for res model {params.model}")
        return mod

    def res_params(self, params: h.primitives.PhysicalResistor.Params) -> ResParams:
        """Convert generic `PhysicalResistor.Params` to PDK `MosParams`."""
        raise NotImplementedError  # FIXME!


def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the {{cookiecutter.pdk_name}} technology"""
    Walker.walk(src)
