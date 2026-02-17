"""
Hdl21 + IHP SG13G2 130nm BiCMOS PDK Modules and Transformations

Defines a set of `hdl21.ExternalModule`s comprising the essential devices of the
IHP SG13G2 130nm BiCMOS PDK, and an `hdl21pdk.netlist` method for converting
process-portable `hdl21.Primitive` elements into these modules.

The SG13G2 PDK features:
- Low-voltage (1.2V) and High-voltage (3.3V) CMOS transistors
- High-performance SiGe:C npn-HBTs with fT up to 350 GHz
- Various passive components (resistors, capacitors, varactors)
- ESD protection devices

Target devices for conversion from `hdl21.Primitive`:
- MOS transistors: sg13_lv_nmos, sg13_lv_pmos, sg13_hv_nmos, sg13_hv_pmos
- Bipolar: npn13G2 variants, pnpMPA
- Resistors: rsil, rhigh, rppd
- Capacitors: cap_cmim, cap_rfcmim
- Diodes: schottky_nbl1, ESD devices
"""

# Std-Lib Imports
from pathlib import Path
from typing import Dict, Optional, Any

# PyPi Imports
from pydantic.dataclasses import dataclass

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import MILLI
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
from .pdk_data import (
    IhpMosParams,
    IhpMosHvParams,
    IhpHbtParams,
    IhpPnpParams,
    IhpResParams,
    IhpCapParams,
    IhpDiodeParams,
)
from .primitives.prim_dicts import *


@dataclass
class Install(PdkInstallation):
    """
    PDK Installation Data for the IHP SG13G2 process.

    This class represents site-specific PDK installation information, including paths to
    the PDK installation and SPICE model libraries. It provides methods to include the
    appropriate model files for different device types and process corners.

    Attributes:
        pdk_path: Path to the IHP-Open-PDK installation (ihp-sg13g2 directory).
        model_lib: Relative path to the ngspice models directory.
    """

    pdk_path: Path  # Path to PDK installation (ihp-sg13g2)
    model_lib: Path  # Relative path to ngspice/models directory

    def include_mos_lv(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the LV MOS model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for LV MOS devices.
        """
        corner_map: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerMOSlv.lib",
            section=corner_map[corner],
        )

    def include_mos_hv(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the HV MOS model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for HV MOS devices.
        """
        corner_map: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerMOShv.lib",
            section=corner_map[corner],
        )

    def include_hbt(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the HBT model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for HBT devices.
        """
        corner_map: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerHBT.lib",
            section=corner_map[corner],
        )

    def include_res(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the resistor model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for resistor devices.
        """
        corner_map: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerRES.lib",
            section=corner_map[corner],
        )

    def include_cap(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the capacitor model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for capacitor devices.
        """
        corner_map: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerCAP.lib",
            section=corner_map[corner],
        )

    def include(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the primary model include for the specified process corner.
        This returns the LV MOS corner by default for compatibility.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include.
        """
        return self.include_mos_lv(corner)

    singleton: Optional["Install"] = None

    @classmethod
    def instance(cls) -> "Install":
        """Get the singleton Install instance."""
        if cls.singleton is None:
            raise ValueError("The Install instance has not been initialized yet.")
        return cls.singleton

    def __post_init__(self):
        if Install.singleton is not None:
            raise ValueError("The Install instance has already been initialized.")
        Install.singleton = self


class IhpWalker(h.HierarchyWalker):
    """
    Hierarchical Walker for IHP SG13G2 PDK.

    Converts `h.Primitive` instances to process-defined `ExternalModule`s
    during circuit compilation.
    """

    def __init__(self):
        super().__init__()
        # Caches of our external module calls
        self.mos_modcalls = dict()
        self.res_modcalls = dict()
        self.cap_modcalls = dict()
        self.diode_modcalls = dict()
        self.bjt_modcalls = dict()

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.Primitive` with IHP `ExternalModule`s."""

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
        """Retrieve or create an `ExternalModule` for MOS parameters `params`."""

        # If model name is specified directly, look it up
        if params.model is not None:
            try:
                return [v for k, v in xtors.items() if params.model in k][0]
            except IndexError:
                msg = f"No Mos module for model name {params.model}"
                raise RuntimeError(msg)

        # Otherwise, select based on MosType, MosVth, MosFamily
        mostype = h.MosType.NMOS if params.tp is None else params.tp
        mosfam = h.MosFamily.CORE if params.family is None else params.family
        mosvth = h.MosVth.STD if params.vth is None else params.vth
        args = (mostype, mosfam, mosvth)

        # Find matching transistor
        subset = {}
        for k, v in xtors.items():
            match = True
            for a in args:
                if a not in k:
                    match = False
                    break
            if match:
                subset[k] = v

        if not subset:
            msg = f"No MOS device found for parameters: type={mostype}, family={mosfam}, vth={mosvth}"
            raise RuntimeError(msg)

        # Return the first match
        return next(iter(subset.values()))

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""

        # Check cache first
        if params in CACHE.mos_modcalls:
            return CACHE.mos_modcalls[params]

        # Get the ExternalModule
        mod = self.mos_module(params)

        # Get default sizes
        w, l = self.use_defaults(params, mod.name, default_xtor_size)

        # Select appropriate parameter class based on device type
        if "hv" in mod.name:
            defaults = IhpMosHvParams.default_instance()
            modparams = IhpMosHvParams(
                w=w,
                l=l,
                ng=params.nf or defaults.ng,
                m=params.mult or defaults.m,
            )
        else:
            defaults = IhpMosParams.default_instance()
            modparams = IhpMosParams(
                w=w,
                l=l,
                ng=params.nf or defaults.ng,
                m=params.mult or defaults.m,
            )

        # Create call, cache, and return
        modcall = mod(modparams)
        CACHE.mos_modcalls[params] = modcall
        return modcall

    def res_module(self, params: PhysicalResistorParams) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for resistor parameters `params`."""

        mod = ress.get(params.model, None)
        if mod is None:
            msg = f"No Res module for model {params.model}. Available: {list(ress.keys())}"
            raise RuntimeError(msg)
        return mod

    def res_module_call(self, params: PhysicalResistorParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for resistor parameters `params`."""

        if params in CACHE.res_modcalls:
            return CACHE.res_modcalls[params]

        mod = self.res_module(params)
        w, l = self.use_defaults(params, mod.name, default_res_size)

        # PhysicalResistorParams doesn't have mult, so default to 1
        modparams = IhpResParams(w=w, l=l, m=1)

        modcall = mod(modparams)
        CACHE.res_modcalls[params] = modcall
        return modcall

    def cap_module(self, params: Any) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for capacitor parameters `params`."""

        mod = caps.get(params.model, None)
        if mod is None:
            # Check varicaps
            mod = varicaps.get(params.model, None)
        if mod is None:
            msg = f"No Cap module for model {params.model}. Available: {list(caps.keys()) + list(varicaps.keys())}"
            raise RuntimeError(msg)
        return mod

    def cap_module_call(self, params: PhysicalCapacitorParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for capacitor parameters `params`."""

        if params in CACHE.cap_modcalls:
            return CACHE.cap_modcalls[params]

        mod = self.cap_module(params)
        w, l = self.use_defaults(params, mod.name, default_cap_size)

        defaults = IhpCapParams.default_instance()
        m = int(params.mult) if params.mult is not None else defaults.m

        modparams = IhpCapParams(w=w, l=l, m=m)

        modcall = mod(modparams)
        CACHE.cap_modcalls[params] = modcall
        return modcall

    def diode_module(self, params: DiodeParams) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for diode parameters `params`."""

        # Check regular diodes first
        mod = diodes.get(params.model, None)
        if mod is None:
            # Check ESD devices
            mod = esd_devices.get(params.model, None)
        if mod is None:
            msg = f"No Diode module for model {params.model}. Available: {list(diodes.keys()) + list(esd_devices.keys())}"
            raise RuntimeError(msg)
        return mod

    def diode_module_call(self, params: DiodeParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for diode parameters `params`."""

        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.diode_module(params)

        defaults = IhpDiodeParams.default_instance()

        if params.w is not None and params.l is not None:
            # Calculate area and perimeter from w/l
            area = params.w * params.l
            pj = 2 * (params.w + params.l)
            modparams = IhpDiodeParams(area=area, pj=pj, m=defaults.m)
        else:
            modparams = IhpDiodeParams()

        modcall = mod(modparams)
        CACHE.diode_modcalls[params] = modcall
        return modcall

    def bjt_module(self, params: BipolarParams) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for bipolar parameters `params`."""

        mod = bjts.get(params.model, None)
        if mod is None:
            # Default to npn13G2 for NPN, pnpMPA for PNP
            if params.tp == h.BipolarType.PNP:
                mod = bjts.get("pnpMPA", None)
            else:
                mod = bjts.get("npn13G2", None)

        if mod is None:
            msg = f"No Bipolar module for model {params.model}. Available: {list(bjts.keys())}"
            raise RuntimeError(msg)
        return mod

    def bjt_module_call(self, params: BipolarParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for bipolar parameters `params`."""

        if params in CACHE.bjt_modcalls:
            return CACHE.bjt_modcalls[params]

        mod = self.bjt_module(params)

        # Determine parameter class based on device type
        if "pnp" in mod.name.lower():
            defaults = IhpPnpParams.default_instance()
            modparams = IhpPnpParams(
                w=defaults.w,
                l=defaults.l,
                m=int(params.mult) if params.mult is not None else defaults.m,
            )
        else:
            defaults = IhpHbtParams.default_instance()
            modparams = IhpHbtParams(
                Nx=defaults.Nx,
                Ny=defaults.Ny,
                m=int(params.mult) if params.mult is not None else defaults.m,
            )

        modcall = mod(modparams)
        CACHE.bjt_modcalls[params] = modcall
        return modcall

    def scale_param(self, orig: Optional[h.Scalar], default: h.Prefixed) -> h.Scalar:
        """
        Scale device parameter value.

        IHP PDK uses microns, so we need to handle unit conversion.
        """
        if orig is None:
            return default
        if isinstance(orig, h.Prefixed):
            return orig
        if isinstance(orig, h.Literal):
            return h.Literal(f"({orig.text} * 1e6)")
        raise TypeError(f"Param Value {orig}")

    def use_defaults(self, params: h.paramclass, modname: str, defaults: dict) -> tuple:
        """Get width and length, using defaults if not specified."""

        w = params.w if params.w is not None else defaults.get(modname, (1.0, 1.0))[0]
        l = params.l if params.l is not None else defaults.get(modname, (1.0, 1.0))[1]

        w = self.scale_param(w, 1000 * MILLI)
        l = self.scale_param(l, 1000 * MILLI)

        return w, l


def compile(src: h.Elaboratables) -> None:
    """
    Compile the given `src` into the IHP SG13G2 technology.

    This function uses the IhpWalker class to walk through the hierarchy of the input
    and replace instances of h.Primitive with IHP-specific ExternalModules.

    Args:
        src: The input source representing the circuit to be compiled.

    Returns:
        None
    """
    IhpWalker().walk(src)
