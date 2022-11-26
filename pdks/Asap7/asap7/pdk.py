""" 
# Hdl21 + ASAP7 PDK Modules and Transformations 

Defines a set of `hdl21.ExternalModule`s comprising the essential devices of the ASAP7 predictive-technology PDK, 
defined at https://github.com/The-OpenROAD-Project/asap7, 
and an `hdl21pdk.netlist` method for converting process-portable `hdl21.Primitive` elements into these modules. 

The primitive components of the ASAP7 PDK are comprised solely of core Mos transistors `{n,p}mos_{rvt,lvt,slvt,sram}`. 

FIXME!: Unlike the common subckt-based models provided by physical PDKs, the ASAP7 transistors are provided solely 
as BSIM-CMG `.model` definitions. These are represented as (FIXME: ...)

"""

import copy
from typing import Union, Optional
from types import SimpleNamespace
from dataclasses import asdict

from pydantic.dataclasses import dataclass

import hdl21 as h
from hdl21.pdk import PdkInstallation
from hdl21.primitives import Mos, MosType, MosVth, MosParams


@dataclass
class Install(PdkInstallation):
    ...  # No content


# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
install: Optional[Install] = None


# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()

_mos_typenames = {
    MosType.NMOS: "n",
    MosType.PMOS: "p",
}
_mos_vtnames = {
    MosVth.STD: "_rvt",
    MosVth.LOW: "_lvt",
    "SLVT": "_slvt",
    "SRAM": "_sram",
}
# Create a lookup table from `MosParams` attributes to `ExternalModule`s
_mos_modules = dict()  # `Dict[(MosType, MosVth), ExternalModule]`, if that worked

# Create each Mos `ExternalModule`
for tp, tpname in _mos_typenames.items():
    for vt, vtname in _mos_vtnames.items():

        modname = f"{tp}mos{vtname}"
        mod = h.ExternalModule(
            domain="asap7",
            name=modname,
            desc=f"ASAP7 PDK Mos {modname}",
            port_list=copy.deepcopy(Mos.port_list),
            paramtype=dict,
        )

        # Add it to the `params => ExternalModules` lookup table
        _mos_modules[(tp, vt)] = mod

        # And add it, with its module-name as key, to the modules namespace
        setattr(modules, modname, mod)


class Asap7Walker(h.HierarchyWalker):
    """Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s."""

    def __init__(self):
        super().__init__()
        # Keep a cache of `ExternalModuleCall`s to avoid creating duplicates
        self.mos_modcalls = dict()

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.primitive.Mos` with our `ExternalModule`s"""
        # Replace transistors
        if call.prim is h.primitives.Mos:
            return self.mos_module_call(call.params)
        # Return everything else as-is
        return call

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        mod = _mos_modules.get((params.tp, params.vth), None)
        if mod is None:
            raise RuntimeError(f"No Mos module {modname}")
        return mod

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in self.mos_modcalls:
            return self.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        # Translate its parameters
        # FIXME: further parameter transformations likely to come
        modparams = asdict(params)
        modparams.pop("vth", None)

        # Combine the two into a call, cache and return it
        modcall = mod(modparams)
        self.mos_modcalls[params] = modcall
        return modcall


def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the ASAP7 technology"""
    Asap7Walker.walk(src)
