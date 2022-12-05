""" 
# Hdl21 Sample PDK
"""

# Std-Lib Imports
import copy
from pathlib import Path
from typing import Optional

# PyPi Imports
from pydantic.dataclasses import dataclass

# Project Imports
import hdl21 as h
from hdl21.primitives import Mos, MosType, MosParams
from hdl21.pdk import PdkInstallation


@dataclass
class Install(PdkInstallation):
    models: Path  # Path to the models file


@h.paramclass
class SamplePdkMosParams:
    """Sample PDK MOS Transistor Parameters"""

    w = h.Param(dtype=Optional[int], desc="Width in resolution units", default=None)
    l = h.Param(dtype=Optional[int], desc="Length in resolution units", default=None)
    npar = h.Param(dtype=Optional[int], desc="Number of parallel fingers", default=None)

    def __post_init_post_parse__(self):
        """Value Checks"""
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
        if params.tp == MosType.PMOS:
            return Pmos
        return Nmos

    def mos_params(self, params: MosParams) -> SamplePdkMosParams:
        """Convert generic primitive `MosParams` into PDK-specific `SamplePdkMosParams`"""
        return SamplePdkMosParams(w=params.w, l=params.l, npar=params.npar)

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
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


def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the Sample technology"""
    return SamplePdkWalker.walk(src)
