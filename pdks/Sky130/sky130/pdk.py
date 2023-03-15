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
from typing import Dict, Tuple, Optional, List
from types import SimpleNamespace

# PyPi Imports
from pydantic.dataclasses import dataclass

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import MEGA, MILLI
from hdl21.pdk import PdkInstallation

PDK_NAME = "sky130"
FIXME = None  # FIXME: Replace with real values!

# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()


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


@h.paramclass
class MosParams:
    """# Sky130 Mos Parameters"""

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=650 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=150 * MILLI)
    nf = h.Param(dtype=h.Scalar, desc="Number of Fingers", default=1)
    mult = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


# FIXME: keep this alias as prior versions may have used it
Sky130MosParams = MosParams


# # Transistors
#
# Mapping from `h.MosType` and `MosVth`s to module-names.
#
MosKey = Tuple[h.MosType, h.MosVth]
xtors: Dict[MosKey, h.ExternalModule] = dict()


def _xtor_module(modname: str, key: Optional[MosKey] = None) -> h.ExternalModule:
    """Transistor module creator, with module-name `name`.
    If optional `MosKey` `key` is provided, adds an entry in the `xtors` dictionary."""

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Mos {modname}",
        port_list=deepcopy(h.Mos.port_list),
        paramtype=MosParams,
    )

    # If given a lookup key, add it to the `xtors` dictionary
    if key is not None:
        if key in xtors:
            msg = f"Internal error: Mos Key {key} has already been defined"
            raise RuntimeError(msg)
        xtors[key] = mod

    # Either way, add it to the `modules` namespace
    setattr(modules, modname, mod)

    return mod


# Add all the transistor entries
_xtor_module("sky130_fd_pr__nfet_01v8", (h.MosType.NMOS, h.MosVth.STD))
_xtor_module("sky130_fd_pr__nfet_01v8_lvt", (h.MosType.NMOS, h.MosVth.LOW))
_xtor_module("sky130_fd_pr__pfet_01v8", (h.MosType.PMOS, h.MosVth.STD))
_xtor_module("sky130_fd_pr__pfet_01v8_hvt", (h.MosType.PMOS, h.MosVth.HIGH))
_xtor_module("sky130_fd_pr__pfet_01v8_lvt", (h.MosType.PMOS, h.MosVth.LOW))
# Note there are no NMOS HVT!
# PMOS LVT was added at some point in history,
# and added to this package in v3.0.


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


class Sky130Walker(h.HierarchyWalker):
    """Hierarchical Walker, converting `h.Primitive` instances to process-defined `ExternalModule`s."""

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.primitive.Mos` with our `ExternalModule`s"""
        # Replace transistors
        if call.prim is h.primitives.Mos:
            return self.mos_module_call(call.params)
        # Return everything else as-is
        return call

    def mos_module_call(self, params: h.primitives.MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in CACHE.mos_modcalls:
            return CACHE.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        # Convert to `mod`s parameter-space
        # Note this silly PDK keeps parameter-values in *microns* rather than SI meters.
        w = self.scale_param(
            params.w, 420 * MILLI
        )  # FIXME: depend on the defaults directly
        l = self.scale_param(params.l, 150 * MILLI)

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

    def mos_module(self, params: h.primitives.MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        mod = xtors.get((params.tp, params.vth), None)
        if mod is None:
            msg = f"No Mos module for model combination {(params.tp, params.vth)}"
            raise RuntimeError(msg)
        return mod

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
    """Compile `src` to the Sample technology"""
    Sky130Walker().walk(src)
