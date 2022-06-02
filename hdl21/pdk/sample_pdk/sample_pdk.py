""" 
# Hdl21 Sample PDK
"""

# Std-Lib Imports
import copy
from typing import Union, Optional

# PyPi Imports
from pydantic.dataclasses import dataclass

# Project Imports
import hdl21 as h
from hdl21.primitives import Mos, MosType, MosParams
from hdl21.pdk import PdkInstallation
from vlsir import circuit as vckt


@dataclass
class Install(PdkInstallation):
    ...  # No content


# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
install: Optional[Install] = None


@h.paramclass
class SamplePdkMosParams:
    """ Sample PDK MOS Transistor Parameters """

    w = h.Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = h.Param(dtype=Optional[int], desc="Length in resolution units", default=None)
    npar = h.Param(dtype=int, desc="Number of parallel fingers", default=1)

    def __post_init_post_parse__(self):
        """ Value Checks """
        if self.w <= 0:
            raise ValueError(f"MosParams with invalid width {self.w}")
        if self.l <= 0:
            raise ValueError(f"MosParams with invalid length {self.l}")
        if self.npar <= 0:
            msg = f"MosParams with invalid number parallel fingers {self.npar}"
            raise ValueError(msg)


# `Pmos` and `Nmos` external modules, each with similar parameter-spaces to `hdl21.primitives.Mos`.
Pmos = h.ExternalModule(
    domain="sample_pdk",
    name="pmos",
    desc=f"Sample PDK Pmos",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=SamplePdkMosParams,
)
Nmos = h.ExternalModule(
    domain="sample_pdk",
    name="nmos",
    desc=f"Sample PDK Nmos",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=SamplePdkMosParams,
)


class SamplePdkWalker(h.HierarchyWalker):
    """ Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s. """

    def __init__(self):
        self.mos_modcalls = dict()

    def visit_instance(self, inst: h.Instance):
        """ Replace instances of `h.Primitive` with our `ExternalModule`s """
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
        """ Retrieve or create an `ExternalModule` for a MOS of parameters `params`. """
        if params.tp == MosType.PMOS:
            return Pmos
        return Nmos

    def mos_params(self, params: MosParams) -> SamplePdkMosParams:
        """ Convert generic primitive `MosParams` into PDK-specific `SamplePdkMosParams` """
        return SamplePdkMosParams(w=params.w, l=params.l, npar=params.npar)

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """ Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in self.mos_modcalls:
            return self.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        # Convert to `mod`s parameter-space
        modparams = self.mos_params(params)

        # Combine the two into a call, cache and return it
        modcall = mod(modparams)
        self.mos_modcalls[params] = modcall
        return modcall


def compile(src: vckt.Package) -> vckt.Package:
    """ Compile proto-Package `src` to the Sample technology """
    ns = h.from_proto(src)
    SamplePdkWalker().visit_namespace(ns)
    return h.to_proto(ns)
