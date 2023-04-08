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
from .pdk_data import *


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
            raise RuntimeError(f"{call.prim} is not legitimate primitive")

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

        # Filter the xtors by a dictionary by partial match
        subset = {
            key: value for key, value in xtors.items() if any(a in key for a in args)
        }

        # More than one answer? You weren't specific enough.
        if len(subset) != 1:
            msg = f"Mos module choice not well-defined given parameters {args}"
            raise RuntimeError(msg)

        return subset.values()[0]

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
            raise TypeError(f"Invalid Scalar parameter {orig}")
        inner = orig.inner
        if isinstance(inner, h.Prefixed):
            return h.Scalar(inner=inner * MEGA)
        if isinstance(inner, h.Literal):
            return h.Scalar(inner=h.Literal(f"({inner} * 1e6)"))
        raise TypeError(f"Param Value {inner}")

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


DEP_CACHE = []


class Sky130DepWalker(h.HierarchyWalker):
    def visit_external_module_call(self, call: h.ExternalModuleCall) -> h.Instantiable:

        name = call.module.name

        if name not in DEP_CACHE:
            DEP_CACHE.append(call.module.name)

        return call


def _remove_duplicates(input_list):
    # Use a set to keep track of the unique elements
    # Order-preserving unique elements are returned
    seen = set()
    return [x for x in input_list if not (x in seen or seen.add(x))]


def _get_file_names(path: Path, substring: str) -> list[str]:
    # Use the glob method to match all files in the given directory
    files = path.glob("*")

    # Convert the matched Path objects to strings if they are files and contain the substring
    file_names = [
        str(file).split("/spice/")[-1]
        for file in files
        if file.is_file() and substring in file.name
    ]

    return file_names


def _find_lines_with_string(file_path: str, search_string: str) -> list:
    # Convert the file_path to a string if it's a Path object
    if isinstance(file_path, Path):
        file_path = str(file_path)

    with open(file_path, "r") as f:
        # Read the file contents and split into lines
        lines = f.readlines()

    # Create a list to store the lines that contain the search string
    matching_lines = []

    # Iterate over each line and check if it contains the search string
    for line in lines:
        if search_string in line:
            matching_lines.append(
                line.strip()
                .split("/spice/")[-1]
                .split(".include")[-1]
                .replace('"', "")
                .strip()
            )  # Append the line (with leading/trailing whitespace removed) to the matching lines list

    return matching_lines


def auto_includes(src: h.sim.Sim, section: str = "tt") -> None:
    """
    Automatically add dependencies to the given `src` based on modules present in the testbench.

    This function updates the `src` object in-place by adding h.sim.Include attributes to it. It first
    walks through the testbench using the Sky130DepWalker class, which populates the DEP_CACHE with
    dependencies. Then, for each dependency, it searches for the appropriate include file and adds
    the corresponding h.sim.Include attribute to the `src` h.sim.Sim object.

    Args:
        src (h.sim.Sim): The object representing the simulation to which the dependencies will be added.
        section (str, optional): The section name used to determine the corner spice file path.
            Defaults to "tt".

    Returns:
        None

    Raises:
        RuntimeError: If no dependencies are found in the testbench.
    """

    # Initialize the section_map dictionary
    section_map = {
        "tt": ["typical", "typical"],
        "sf": ["typical", "typical"],
        "ff": ["typical", "typical"],
        "sf": ["typical", "typical"],
        "fs": ["typical", "typical"],
        "hh": ["high", "high"],
        "hl": ["high", "low"],
        "lh": ["low", "high"],
        "ll": ["low", "low"],
    }

    if section[0] != "h" or section[0] != "l":
        fet_section = section
    else:
        fet_section = "tt"

    install = Install.instance()  # Obtain the singleton instance of the Install class

    Sky130DepWalker().walk(
        src.Tb
    )  # Walk through the Testbench hierarchy to collect dependencies

    src.attrs.append(h.sim.Literal(".control"))
    src.attrs.append(h.sim.Literal("set ng_nomodcheck"))
    src.attrs.append(h.sim.Literal("set ngbehavior=hsa"))
    src.attrs.append(h.sim.Literal(".endc"))

    # Boilerplate Spice includes to make sure the simulation runs
    src.attrs.append(h.sim.Options(scale=1e-6))

    # Check if Mismatch Monte Carlo is required
    if section[:-2] == "mm":
        src.attrs.append(h.sim.Param(1, name="mc_mm_switch"))
    else:
        src.attrs.append(h.sim.Param(0, name="mc_mm_switch"))

    # Check if Process variation Monte Carlo is required
    IS_PR = False
    if section == "mc":
        src.attrs.append(h.sim.Param(1, name="mc_pr_switch"))
        IS_PR = True
    else:
        src.attrs.append(h.sim.Param(0, name="mc_pr_switch"))

    src.attrs.append(
        h.sim.Include(
            install.pdk_path / install.lib_path.parent / "parameters/lod.spice"
        )
    )

    if DEP_CACHE == []:
        raise RuntimeError("No dependencies found in testbench.")

    full_incs = []
    incs = []

    # full_incs.append(f"/usr/local/share/pdk/sky130A/libs.tech/ngspice/corners/{section}/specialized_cells.spice")

    # Iterate over the collected dependencies
    for dep in DEP_CACHE:

        if "fet" in dep:

            # For the exceptional cases, add the appropriate spice file
            if "20v0" in dep:

                # No iso or zvt corner files for 20v0
                if "iso" in dep or "zvt" in dep:
                    d = dep[:-4]
                else:
                    d = dep

                incs.append(f"{d}__{fet_section}_discrete.corner.spice")
                incs.append("sky130_fd_pr__diode_pw2nd_05v5.model.spice")

            elif "pfet_g5v0d16v0" in dep:
                incs.append("sky130_fd_pr__pfet_g5v0d16v0__subcircuit.pm3.spice")
                incs.append("sky130_fd_pr__pfet_g5v0d16v0.pm3.spice")
                incs.append(f"sky130_fd_pr__pfet_g5v0d16v0__{fet_section}.corner.spice")
                incs.append(
                    "sky130_fd_pr__pfet_g5v0d16v0__parasitic__diode_pw2dn.model.spice"
                )

            else:

                # Iterate over lines found in the corner spice file
                for f in _find_lines_with_string(
                    install.pdk_path
                    / install.lib_path.parent
                    / Path(f"corners/{section}.spice"),
                    dep + "__",
                ):
                    incs.append(f)

            full_incs.append(
                str(
                    install.pdk_path
                    / install.lib_path.parent
                    / f"corners/{fet_section}/nonfet.spice"
                )
            )

        elif "parasitic" in dep:

            # Iterate over lines found in the corner spice file
            for f in _find_lines_with_string(
                install.pdk_path / install.lib_path.parent / Path("all.spice"),
                dep,
            ):
                full_incs.append(str(install.pdk_path / install.lib_path.parent / f))

        elif "res" in dep or "cap" in dep or "diode_pw2" in dep:

            r = section_map[section[:2]][0]
            c = section_map[section[:2]][1]

            full_incs.append(
                str(
                    install.pdk_path
                    / install.lib_path.parent
                    / "r+c/"
                    / f"res_{r}__cap_{c}.spice"
                )
            )
            full_incs.append(
                str(
                    install.pdk_path
                    / install.lib_path.parent
                    / "r+c/"
                    / f"res_{r}__cap_{c}__lin.spice"
                )
            )
            full_incs.append(
                str(
                    install.pdk_path
                    / install.lib_path.parent
                    / "sky130_fd_pr__model__r+c.model.spice"
                )
            )

            # Iterate over lines found in the all.spice file
            for f in _find_lines_with_string(
                install.pdk_path / install.lib_path.parent / Path("all.spice"),
                dep,
            ):
                incs.append(f)

    full_incs.append(
        str(install.pdk_path / install.lib_path.parent / "parameters/invariant.spice")
    )

    # Include critical.spice and montecarlo.spice files if Process variation Monte Carlo is enabled
    if IS_PR:
        src.attrs.append(
            h.sim.Include(install.pdk_path / install.lib_path.parent / "critical.spice")
        )
        src.attrs.append(
            h.sim.Include(
                install.pdk_path / install.lib_path.parent / "montecarlo.spice"
            )
        )

    # Reduce to only unique elements
    incs = _remove_duplicates(incs)
    full_incs = _remove_duplicates(full_incs)

    # Add Include objects to the src.attrs list with the appropriate file paths
    for inc in full_incs:
        src.attrs.append(h.sim.Include(inc))

    for inc in incs:
        src.attrs.append(h.sim.Include(install.pdk_path / install.model_ref / inc))
