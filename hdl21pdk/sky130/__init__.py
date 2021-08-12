""" 
Sky130 PDK Transformer 
"""

import sys, copy
from typing import Union

import hdl21pdk
import hdl21 as h
from hdl21.primitives import Mos, MosType, MosVth, MosParams


class Sky130Walker(h.HierarchyWalker):
    """Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s."""

    def __init__(self):
        self.sources = set()
        self.mos_modules = dict()
        self.mos_modcalls = dict()

    def visit_instance(self, inst: h.Instance):
        """Replace instances of `h.Primitive` with our `ExternalModule`s"""
        if isinstance(inst.of, h.PrimitiveCall):
            inst.of = self.replace_primitive(inst.of)
            return
        # Otherwise keep traversing, instance unmodified
        return super().visit_instance(inst)

    def replace_primitive(
        self, primcall: h.PrimitiveCall
    ) -> Union[h.ExternalModuleCall, h.PrimitiveCall]:
        # Replace transistors
        if primcall.prim is h.primitives.Mos:
            return self.mos_module_call(primcall.params)
        # Return everything else as-is
        return primcall

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        # First check our cache
        key = (params.tp, params.vth)
        if key in self.mos_modules:
            return self.mos_modules[key]

        # Not yet encountered. Create a new `ExternalModule`.
        # First sort out its name.
        modname = "nmos4_" if params.tp == MosType.NMOS else "pmos4_"
        if isinstance(params.vth, str):
            modname += params.vth
        elif params.vth == MosVth.STD:
            modname += "standard"

        # Create the module definition
        mod = h.ExternalModule(
            name=modname,
            desc=f"Sky130 PDK {modname}",
            port_list=copy.copy(Mos.port_list),
        )
        # Store it in our cache
        self.mos_modules[key] = mod
        # And return it
        return mod

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        # First check our cache
        if params in self.mos_modcalls:
            return self.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)
        # Create the parameter-dictionary
        modparams = dict(
            w="130n" if params.w is None else f"'{params.w} 1e6'",
            l="130n" if params.w is None else f"'{params.l} 1e6'",
            m=params.npar,
            mult=1,
        )
        # Combine the two into a call, store and return it
        modcall = mod(**modparams)
        self.mos_modcalls[params] = modcall
        return modcall


def compile(src: h.proto.Package) -> h.proto.Package:
    """Compile proto-Package `src` to Sky130"""
    ns = h.from_proto(src)
    Sky130Walker().visit_namespace(ns)
    print(ns)
    return h.to_proto(ns)


# Register as a PDK module
hdl21pdk.register(sys.modules[__name__])
