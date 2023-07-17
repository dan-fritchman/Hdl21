import hdl21 as h
from .primitives.prim_dicts import *


@dataclass
class Install(PdkInstallation):
    """Pdk Installation Data
    External data provided by site-specific installations"""

    model_lib: Path  # Path to the transistor models included in this module

    def include_design(self) -> h.sim.Include:
        return h.sim.Include(path=self.model_lib.parent / "design.ngspice")

    def include_mos(self, corner: h.pdk.CmosCorner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for MOSFETs"""

        mos_corners: Dict[h.pdk.CmosCorner, str] = {
            h.pdk.CmosCorner.TT: "typical",
            h.pdk.CmosCorner.FF: "ff",
            h.pdk.CmosCorner.SS: "ss",
            h.pdk.CmosCorner.FS: "fs",
            h.pdk.CmosCorner.SF: "sf",
        }
        return h.sim.Lib(path=self.model_lib, section=mos_corners[corner])

    def include_resistors(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for Resistors"""

        res_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "res_typical",
            h.pdk.Corner.FAST: "res_ff",
            h.pdk.Corner.SLOW: "res_ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in res_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=res_corners[corner])

    def include_diodes(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for Diodes"""

        diode_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "diode_typical",
            h.pdk.Corner.FAST: "diode_ff",
            h.pdk.Corner.SLOW: "diode_ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in diode_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=diode_corners[corner])

    def include_bjts(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for BJTs"""

        bjt_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "bjt_typical",
            h.pdk.Corner.FAST: "bjt_ff",
            h.pdk.Corner.SLOW: "bjt_ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in bjt_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=bjt_corners[corner])

    def include_moscaps(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """# Get the model include file for process corner `corner` for MOS Capacitors"""

        moscap_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "moscap_typical",
            h.pdk.Corner.FAST: "moscap_ff",
            h.pdk.Corner.SLOW: "moscap_ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in moscap_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=moscap_corners[corner])

    def include_mimcaps(self, corner: h.pdk.Corner) -> h.sim.Lib:
        mimcap_corners: Dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "mimcap_typical",
            h.pdk.Corner.FAST: "mimcap_ff",
            h.pdk.Corner.SLOW: "mimcap_ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in mimcap_corners:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(path=self.model_lib, section=mimcap_corners[corner])


class Gf180Walker(h.HierarchyWalker):
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
            return call

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for a MOS of parameters `params`."""
        if params.model is not None:
            try:
                return [v for k, v in xtors.items() if params.model in k][0]
            except IndexError:
                msg = f"No Mos module for model name {(params.model)}"
                raise RuntimeError(msg)

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

        if len(subset) >= 2:
            msg = f"Mos module choice not well-defined given parameters {args}"
            raise RuntimeError(msg)

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

        # Convert to `mod`s parameter-space
        w, l = self.use_defaults(params, mod.name, default_xtor_size)

        modparams = GF180MosParams(
            w=w,
            l=l,
            nf=params.npar,  # FIXME: renaming?
            m=params.mult,
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

        w, l = self.use_defaults(params, mod.name, default_res_size)

        modparams = GF180ResParams(r_width=w, r_length=l)

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
        # First check our cache
        if params in CACHE.cap_modcalls:
            return CACHE.cap_modcalls[params]

        mod = self.cap_module(params)

        w = self.scale_param(params.w, 1000 * MILLI)
        l = self.scale_param(params.l, 1000 * MILLI)

        modparams = GF180CapParams(c_width=w, c_length=l)

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
        # First check our cache
        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.diode_module(params)

        w, l = self.use_defaults(params, mod.name, default_diode_size)

        modparams = GF180DiodeParams(area=w * l, pj=2 * w + 2 * l)

        modcall = mod(modparams)
        CACHE.diode_modcalls[params] = modcall
        return modcall

    def bjt_module(self, params: BipolarParams):
        """Retrieve or create an `ExternalModule` for a Bipolar of parameters `params`."""
        mod = bjts.get(params.model, None)

        if mod is None:
            msg = f"No Bipolar module for model combination {(params.model, params.tp)}"
            raise RuntimeError(msg)

        return mod

    def bjt_module_call(self, params: BipolarParams):
        # First check our cache
        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.bjt_module(params)

        modparams = GF180BipolarParams(m=params.mult or 1)

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

        return w, l


def compile(src: h.Elaboratables) -> None:
    """Compile `src` to the Sample technology"""
    Gf180Walker().walk(src)
