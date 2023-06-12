""" 
# Hdl21 Sample PDK

A non-physical, 110% made-up process technology, designed solely for demonstrating the `hdl21.pdk` interface. 
The Hdl21 sample PDK is integrated in the Hdl21 package, and is therefore available to every installation of Hdl21. 

It includes: 
* Nmos and Pmos transistor `ExternalModule`s
* Similar transistor modules, defined as SPICE primitive-MOS models
* Comilation from `hdl21.primitives` to the PDK modules 
* An `Install` type, demonstrating typical usage of out-of-Python PDK installation data 
* A built-in model file, compatible with all supported simulators

Note that unlike most Hdl21 PDKs, the content of `sample_pdk.install` - the model file - 
*is* built into the source tree, and is configured at import-time. 
For most PDKs in which this data is distributed separately, 
a site-specific `sitepdks` module customarily configures the `install` variable.

"""

# Std-Lib Imports
import copy
from pathlib import Path

# PyPi Imports
from pydantic.dataclasses import dataclass

# Project Imports
import hdl21 as h
from hdl21.prefix import µ
from hdl21.primitives import Mos, MosType, MosParams as PrimMosParams
from hdl21.pdk import PdkInstallation
from vlsirtools import SpiceType


@dataclass
class Install(PdkInstallation):
    models: Path  # Path to the models file


@h.paramclass
class SamplePdkMosParams:
    """Sample PDK MOS Transistor Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in resolution units", default=1 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length in resolution units", default=1 * µ)
    nf = h.Param(dtype=h.Scalar, desc="Number of parallel fingers", default=1)
    m = h.Param(dtype=h.Scalar, desc="Number of parallel fingers", default=1)

    def __post_init_post_parse__(self):
        """Value Checks"""
        if self.w <= 0:
            raise ValueError(f"MosParams with invalid width {self.w}")
        if self.l <= 0:
            raise ValueError(f"MosParams with invalid length {self.l}")
        if self.nf <= 0:
            msg = f"MosParams with invalid number parallel fingers {self.nf}"
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

# `PmosModel` and `NmosModel` also external modules, referring directly to the SPICE "primitive MOS" M-elements.
PmosModel = h.ExternalModule(
    domain="sample_pdk",
    name="pmos_model",
    desc=f"Sample PDK Pmos (Model M-Element)",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=SamplePdkMosParams,
    spicetype=SpiceType.MOS,
)
NmosModel = h.ExternalModule(
    domain="sample_pdk",
    name="nmos_model",
    desc=f"Sample PDK Nmos (Model M-Element)",
    port_list=copy.deepcopy(Mos.port_list),
    paramtype=SamplePdkMosParams,
    spicetype=SpiceType.MOS,
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

    def mos_module(self, params: PrimMosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        if params.tp == MosType.PMOS:
            return Pmos
        return Nmos

    def mos_params(self, params: PrimMosParams) -> SamplePdkMosParams:
        """Convert generic primitive `MosParams` into PDK-specific `SamplePdkMosParams`"""
        # FIXME: pending rename of `primitives.MosParams.npar`
        # FIXME: map parameters using the `default` field directly; needs debug
        w = params.w or 1 * µ
        l = params.l or 1 * µ
        m = params.mult or 1
        nf = params.npar or 1
        return SamplePdkMosParams(w=w, l=l, m=m, nf=nf)

    def mos_module_call(self, params: PrimMosParams) -> h.ExternalModuleCall:
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
