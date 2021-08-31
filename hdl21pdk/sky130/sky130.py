""" 
Sky130 PDK Transformer 
"""

import sys, copy
from typing import Union, IO

import hdl21pdk
import hdl21 as h
from hdl21.primitives import Mos, MosType, MosVth, MosParams
from hdl21.netlist import NetlistFormat


@h.paramclass
class Sky130MosParams:
    """ Parameters for the PDK MOS transistor modules """

    w = h.Param(dtype=str, desc="Width, in PDK Units (microns)")
    l = h.Param(dtype=str, desc="Length, in PDK Units (microns)")
    m = h.Param(dtype=int, desc="Multiplier", default=1)
    mult = h.Param(dtype=int, desc="(Another?) Multiplier", default=1)


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
        modname = "n" if params.tp == MosType.NMOS else "p"

        if params.vth == MosVth.STD:
            modname += "short"
        elif params.vth == MosVth.HIGH:
            modname += "hv"
        else:
            raise ValueError(f"Invalid or unsupported MosVth {params.vth}")

        # Create the module definition
        mod = h.ExternalModule(
            domain="sky130",
            name=modname,
            desc=f"Sky130 PDK {modname}",
            port_list=copy.copy(Mos.port_list),
            paramtype=Sky130MosParams,
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
        # Convert to `mod`s parameter-space
        # Note this silly PDK keeps parameter-values in *microns* rather than SI meters.
        modparams = Sky130MosParams(
            w="(650n * 1e6)" if params.w is None else f"({params.w} * 1e6)",
            l="(150n * 1e6)" if params.w is None else f"({params.l} * 1e6)",
            m=params.npar,
            mult=1,
        )
        # Combine the two into a call, store and return it
        modcall = mod(modparams)
        self.mos_modcalls[params] = modcall
        return modcall


def compile(src: h.proto.Package) -> h.proto.Package:
    """Compile proto-Package `src` to Sky130"""
    ns = h.from_proto(src)
    Sky130Walker().visit_namespace(ns)
    return h.to_proto(ns)


def netlist(src: h.proto.Package, target: IO, fmt: NetlistFormat) -> None:
    ns = h.from_proto(src)
    walker = Sky130Walker()
    walker.visit_namespace(ns)
    compiled = h.to_proto(ns)

    # Cheating for now, gotta figure out sad netlist things like library-corners
    ext_sources = set()
    for emod in walker.mos_modules.values():
        ext_sources.add(source(emod, fmt))
    for esrc in ext_sources:
        target.write(f'include "{esrc}" section=tt_fet \n')
    target.write(f"\n\n")

    h.netlist(compiled, target, fmt)


def source(emod: h.ExternalModule, fmt: NetlistFormat) -> str:
    """ Get the (external) source for Module `emod` in format `fmt`. """
    return "NotImplemented (safely) sorry"  # FIXME!

