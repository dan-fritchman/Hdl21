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

import copy
from pathlib import Path
from typing import Union, Dict, Tuple, Optional
from types import SimpleNamespace

from pydantic.dataclasses import dataclass

import hdl21 as h
from hdl21.pdk import PdkInstallation
from hdl21.primitives import Mos, MosType, MosVth, MosParams
from vlsir import circuit as vckt


@dataclass
class Install(PdkInstallation):
    """ Pdk Installation Data 
    External data provided by site-specific installations """

    model_lib: Path  # Path to the transistor models included in this module


@h.paramclass
class Sky130MosParams:
    """ Parameters for the PDK MOS transistor modules """

    # l = 1 w = 1 ad = 0 as = 0 pd = 0 ps = 0 nrd = 0 nrs = 0 sa = 0 sb = 0 sd = 0 mult = 1 nf = 1.0

    w = h.Param(dtype=str, desc="Width, in PDK Units (microns)", default=1)
    l = h.Param(dtype=str, desc="Length, in PDK Units (microns)", default=1)
    nf = h.Param(dtype=int, desc="Number of Fingers", default=1)
    mult = h.Param(dtype=int, desc="Multiplier", default=1)


def _xtor_module(modname: str) -> h.ExternalModule:
    """ Transistor module creator, with module-name `name`."""
    return h.ExternalModule(
        domain="sky130",
        name=modname,
        desc=f"Sky130 PDK Mos {modname}",
        port_list=copy.deepcopy(Mos.port_list),
        paramtype=Sky130MosParams,
    )


# # Transistors
#
# Mapping from `MosType` and `MosVth`s to module-names.
#
xtors: Dict[Tuple[MosType, MosVth], h.ExternalModule] = {
    (MosType.NMOS, MosVth.STD): _xtor_module("sky130_fd_pr__nfet_01v8"),
    (MosType.NMOS, MosVth.LOW): _xtor_module("sky130_fd_pr__nfet_01v8_lvt"),
    (MosType.PMOS, MosVth.STD): _xtor_module("sky130_fd_pr__pfet_01v8"),
    (MosType.PMOS, MosVth.HIGH): _xtor_module("sky130_fd_pr__pfet_01v8_hvt"),
    # Note there are no NMOS HVT or PMOS LVT!
}

# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()
for xtor in xtors.values():
    # Add each to the `modules` namespace
    setattr(modules, xtor.name, xtor)


class Sky130Walker(h.HierarchyWalker):
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
        mod = xtors.get((params.tp, params.vth), None)
        if mod is None:
            raise RuntimeError(
                f"No Mos module for model combination {(params.tp, params.vth)}"
            )
        return mod

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """ Retrieve or create a `Call` for MOS parameters `params`."""
        # First check our cache
        if params in self.mos_modcalls:
            return self.mos_modcalls[params]

        # Not found; create a new `ExternalModuleCall`.
        # First retrieve the `ExternalModule`.
        mod = self.mos_module(params)

        # Convert to `mod`s parameter-space
        # Note this silly PDK keeps parameter-values in *microns* rather than SI meters.
        w = "650n" if params.w is None else params.w
        l = "150n" if params.l is None else params.l
        modparams = Sky130MosParams(
            w=f"({w} * 1e6)", l=f"({l} * 1e6)", nf=params.npar, mult=1,
        )

        # Combine the two into a call, cache and return it
        modcall = mod(modparams)
        self.mos_modcalls[params] = modcall
        return modcall


def compile(src: vckt.Package) -> vckt.Package:
    """ Compile proto-Package `src` to the SkyWater 130nm technology """
    ns = h.from_proto(src)
    Sky130Walker().visit_namespace(ns)
    return h.to_proto(ns)
