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
from pathlib import Path
from typing import Dict, Optional, Any

# PyPi Imports
from pydantic.dataclasses import dataclass

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import MILLI, TERA, MEGA
from hdl21.pdk import PdkInstallation
from hdl21.primitives import (
    Mos,
    PhysicalResistor,
    PhysicalCapacitor,
    Diode,
    Bipolar,
    ThreeTerminalResistor,
    ThreeTerminalCapacitor,
    MosParams,
    PhysicalResistorParams,
    PhysicalCapacitorParams,
    DiodeParams,
    BipolarParams,
)

# Import relevant data from the PDK's data module
from .primitives.prim_dicts import *


@dataclass
class Install(PdkInstallation):
    """
    PDK Installation Data for the Sky130 process.

    This class represents site-specific PDK installation information, including paths to
    the PDK installation, library files, and SPICE models reference. It also provides a
    method to include the appropriate model files for a given process corner.

    Attributes:
        pdk_path (Path): Path to the PDK installation.
        lib_path (Path): Relative path to the PDK ngspice library file.
        model_ref (Path): Relative path to the PDK SPICE models reference.
    """

    pdk_path: Path  # Path to PDK installation
    lib_path: Path  # Relative path to PDK ngpisce library file
    model_ref: Path  # Relative path to PDK SPICE models reference

    def include(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the model include file for the specified process corner.

        This method returns the appropriate model include file for the given process corner.
        It checks if the provided corner is a valid h.pdk.Corner instance and raises a
        ValueError if it is not.

        Args:
            corner (h.pdk.Corner): The process corner for which to retrieve the model include file.

        Returns:
            h.sim.Lib: The model include file for the specified process corner.

        Raises:
            ValueError: If an invalid process corner is provided.
        """

        mos_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in mos_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.lib_path, section=mos_corners[corner]
        )

    singleton: Optional["Install"] = None

    @classmethod
    def instance(cls) -> "Install":
        if cls.singleton is None:
            raise ValueError("The Install instance has not been initialized yet.")
        return cls.singleton

    def __post_init__(self):
        if Install.singleton is not None:
            raise ValueError("The Install instance has already been initialized.")
        Install.singleton = self


class Sky130Walker(h.HierarchyWalker):
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
        """Replace instances of `h.primitive.Mos` with our `ExternalModule`s"""
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
            # Return everything else as-is
            return call

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        if params.model is not None:

            try:
                return [v for k, v in xtors.items() if params.model in k][0]
            except IndexError:
                msg = f"No Mos module for model name {(params.model)}"
                raise RuntimeError(msg)

        """
        Here we wittle down our list of potential candidates

        General parameters we're concerned with are:

        1) h.MosType - Most important decision is it a PMOS or an NMOS, default = NMOS
        2) h.MosFamily - Detemines what class of transistor, CORE, IO, HVT, default = CORE
        3) h.MosVth - Mos Threshold, HIGH, STD, LOW, ULTRA_LOW, default = STD
        """

        # Map none to default, otherwise leave alone
        mostype = h.MosType.NMOS if params.tp is None else params.tp
        mosfam = h.MosFamily.CORE if params.family is None else params.family
        mosvth = h.MosVth.STD if params.vth is None else params.vth
        args = (mostype, mosfam, mosvth)

        # Find all the xtors that match the args
        subset = {}
        for k, v in xtors.items():

            match = False
            for a in args:
                if a not in k:
                    break
            else:
                match = True

            if match:
                subset[k] = v

        # FIXME: Probably should be an error...
        # if len(subset) > 2:
        #     msg = f"Mos module choice not well-defined given parameters {args}"
        #     raise RuntimeError(msg)

        # Return the first one (supported as of 3.7)
        return next(iter(subset.values()))

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in CACHE.mos_modcalls:
            return CACHE.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        w, l = self.use_defaults(params, mod.name, default_xtor_size)

        # Select appropriate parameters for 20V/ESD-G5V0D10V5 mosfets
        if "20v" in mod.name:

            modparams = Sky130Mos20VParams(w=w, l=l, m=params.mult)

        else:

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

        if mod.paramtype == Sky130GenResParams:

            w, l = self.use_defaults(params, mod.name, default_gen_res_size)

            modparams = Sky130GenResParams(w=w, l=l)

        elif mod.paramtype == Sky130PrecResParams:

            l = default_prec_res_L[mod.name]

            modparams = Sky130PrecResParams(l=l)

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

        if params in CACHE.cap_modcalls:
            return CACHE.cap_modcalls[params]

        mod = self.cap_module(params)

        m = 1

        if params.mult is not None:

            m = int(params.mult)

        if mod.paramtype == Sky130MimParams:

            w, l = self.use_defaults(params, mod.name, default_cap_sizes)
            modparams = Sky130MimParams(w=w, l=l, mf=m)

        elif mod.paramtype == Sky130VarParams:

            w, l = self.use_defaults(params, mod.name, default_cap_sizes)
            modparams = Sky130VarParams(w=w, l=l, vm=m)

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

        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.diode_module(params)

        if params.w is not None and params.w is not None:

            # This scaling is a quirk of SKY130
            a = params.w * params.l * 1 * TERA
            pj = 2 * (params.w + params.l) * MEGA
            modparams = Sky130DiodeParams(area=a, pj=pj)

        else:

            modparams = Sky130DiodeParams()

        modcall = mod(modparams)
        CACHE.diode_modcalls[params] = modcall
        return modcall

    def bjt_module(self, params: BipolarParams):
        """Retrieve or create an `ExternalModule` for a Bipolar of parameters `params`."""
        mod = bjts.get(params.model, None)

        if mod is None:
            msg = f"No Bipolar module for model {params.model}"
            raise RuntimeError(msg)

        return mod

    def bjt_module_call(self, params: BipolarParams):

        if params in CACHE.bjt_modcalls:
            return CACHE.bjt_modcalls[params]

        mod = self.bjt_module(params)

        if params.mult is not None:
            mult = int(params.mult)
        else:
            mult = 1

        modparams = Sky130BipolarParams(m=mult)

        modcall = mod(modparams)
        CACHE.bjt_modcalls[params] = modcall
        return modcall

    def scale_param(self, orig: Optional[h.Scalar], default: h.Prefixed) -> h.Scalar:
        """Replace device size parameter-value `orig`.
        Primarily type-dispatches across the need to scale to microns for this PDK."""
        if orig is None:
            return default
        if not isinstance(orig, h.Scalar):
            orig = h.scalar.to_scalar(orig)

        if isinstance(orig, h.Prefixed):
            return orig
        if isinstance(orig, h.Literal):
            return h.Literal(f"({orig} * 1e6)")
        raise TypeError(f"Param Value {orig}")

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

        w = self.scale_param(w, 1000 * MILLI)
        l = self.scale_param(l, 1000 * MILLI)

        return w, l


def compile(src: h.Elaboratables) -> None:
    """
    Compile the given `src` into the Sample technology using the Sky130 process.

    This function uses the Sky130Walker class to walk through the hierarchy of the input `src`
    and replace instances of h.Primitive with process-defined ExternalModules. The Sky130Walker
    class takes care of replacing different primitive components such as MOS transistors, resistors,
    capacitors, diodes, and bipolar junction transistors with their respective Sky130 technology
    counterparts.

    Args:
        src (h.Elaboratables): The input source representing the circuit to be compiled
            into the Sample technology using the Sky130 process.

    Returns:
        None
    """

    Sky130Walker().walk(src)
