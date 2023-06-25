# Std-Lib Imports
from copy import deepcopy
from dataclasses import field
from typing import Dict, Tuple, List
from types import SimpleNamespace

# PyPi Imports
from pydantic.dataclasses import dataclass

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import (
    MILLI,
    µ,
    MEGA,
    TERA,
)
from hdl21.primitives import (
    MosType,
    MosVth,
    MosFamily,
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

# Vlsirtool Types to ease downstream parsing
from vlsirtools import SpiceType

FIXME = None  # FIXME: Replace with real values!
PDK_NAME = "sky130"

"""
The following section contains all the necessary @paramclasses required to describe
parameters of devices in the Sky130 Open PDK. It contains params:

- MosParams (aka. Sky130MosParams) - standard MOS device parameters
- Sky130Mos20VParams - special parameters for 20V MOS devices
- Sky130GenResParams - parameters for generic resistors
- Sky130PrecResParams - parameters for Sky130's precision resistors
- Sky130MimParams - parameters for  Metal-insulator-Metal (MiM) capacitors
- Sky130VarParams - paramaters foVPWRr variable capacitors (ie. varactors)
- Sky130VPPParams - parameters for both Vertical Perpendicular Plate (VPP) and Vertical Parallel Plate (VPP) capacitors
- Sky130DiodeParams - parameters for diodes
- Sky130BipolarParams - parameters for bipolar devices
- Sky130LogicParams - parameters for logic devices
"""


@h.paramclass
class MosParams:
    """
    A parameter class representing the MOSFET parameters for the Sky130 technology.
    These parameters include various geometrical and electrical props of the MOSFET device,
    such as width, length, number of fingers, drain and source areas, drain and source perimeters,
    resistive values, spacings, and multipliers.

    Attributes:
    w (h.Scalar): Width of the MOSFET in PDK Units (µm). Default is 650 * MILLI.
    l (h.Scalar): Length of the MOSFET in PDK Units (µm). Default is 150 * MILLI.
    nf (h.Scalar): Number of fingers in the MOSFET. Default is 1.
    m (h.Scalar): Multiplier for the MOSFET (alias for mult). Default is 1.

    #! CAUTION: The following parameters are not recommended for design use.

    ad (h.Literal): Drain area of the MOSFET. Default is 'int((nf+1)/2) * w/nf * 0.29'.
    As (h.Literal): Source area of the MOSFET. Default is 'int((nf+2)/2) * w/nf * 0.29'.
    pd (h.Literal): Drain perimeter of the MOSFET. Default is '2int((nf+1)/2) * (w/nf + 0.29)'.
    ps (h.Literal): Source perimeter of the MOSFET. Default is '2int((nf+2)/2) * (w/nf + 0.29)'.
    nrd (h.Literal): Drain resistive value of the MOSFET. Default is '0.29 / w'.
    nrs (h.Literal): Source resistive value of the MOSFET. Default is '0.29 / w'.
    sa (h.Scalar): Spacing between adjacent gate to drain. Default is 0.
    sb (h.Scalar): Spacing between adjacent gate to source. Default is 0.
    sd (h.Scalar): Spacing between adjacent drain to source. Default is 0.
    mult (h.Scalar): Multiplier for the MOSFET. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=650 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=150 * MILLI)
    nf = h.Param(dtype=h.Scalar, desc="Number of Fingers", default=1)
    ad = h.Param(
        dtype=h.Literal,
        desc="Drain Area",
        default=h.Literal("int((nf+1)/2) * w/nf * 0.29"),
    )

    # This unfortunate naming is to prevent conflicts with base python.
    As = h.Param(
        dtype=h.Literal,
        desc="Source Area",
        default=h.Literal("int((nf+2)/2) * w/nf * 0.29"),
    )

    pd = h.Param(
        dtype=h.Literal,
        desc="Drain Perimeter",
        default=h.Literal("2*int((nf+1)/2) * (w/nf + 0.29)"),
    )
    ps = h.Param(
        dtype=h.Literal,
        desc="Source Perimeter",
        default=h.Literal("2*int((nf+2)/2) * (w/nf + 0.29)"),
    )
    nrd = h.Param(
        dtype=h.Literal, desc="Drain Resistive Value", default=h.Literal("0.29 / w")
    )
    nrs = h.Param(
        dtype=h.Literal, desc="Source Resistive Value", default=h.Literal("0.29 / w")
    )
    sa = h.Param(
        dtype=h.Scalar,
        desc="Spacing between Adjacent Gate to Drain",
        default=h.Literal(0),
    )
    sb = h.Param(
        dtype=h.Scalar,
        desc="Spacing between Adjacent Gate to Source",
        default=h.Literal(0),
    )
    sd = h.Param(
        dtype=h.Scalar,
        desc="Spacing between Adjacent Drain to Source",
        default=h.Literal(0),
    )
    mult = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


# FIXME: keep this alias as prior versions may have used it
Sky130MosParams = MosParams


@h.paramclass
class Sky130Mos20VParams:
    """
    A parameter class representing the MOSFET parameters for the Sky130 technology with a 20V rating.
    These parameters include the width, length, and multiplier of the MOSFET device.

    Attributes:
    w (h.Scalar): Width of the MOSFET in PDK Units (µm). Default is 30.
    l (h.Scalar): Length of the MOSFET in PDK Units (µm). Default is 1.
    m (h.Scalar): Multiplier for the MOSFET. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=30)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class Sky130GenResParams:
    """
    A parameter class representing the generic resistor parameters for the Sky130 technology. These parameters include the width, length, and multiplicity of the resistor device.

    Attributes:
    w (h.Scalar): Width of the resistor in PDK Units (µm). Default is 1000 * MILLI.
    l (h.Scalar): Length of the resistor in PDK Units (µm). Default is 1000 * MILLI.
    m (h.Scalar): Multiplicity of the resistor. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    m = h.Param(dtype=h.Scalar, desc="Multiplicity", default=1)


@h.paramclass
class Sky130PrecResParams:
    """
    A parameter class representing the precision resistor parameters for the Sky130 technology.
    These parameters include the length and multiplicity of the precision resistor device.

    Attributes:
    l (h.Scalar): Length of the precision resistor in PDK Units (µm). Default is 1000 * MILLI.
    mult (h.Scalar): Multiplicity of the precision resistor. Default is 1.
    m (h.Scalar): Multiplicity of the precision resistor (alias for mult). Default is 1.
    """

    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    mult = h.Param(dtype=h.Scalar, desc="Multiplicity", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplicity", default=1)


@h.paramclass
class Sky130MimParams:
    """
    A parameter class representing the MiM (Metal-insulator-Metal) capacitor parameters for the Sky130 technology.
    These parameters include the width, length, and multiplier of the MiM capacitor device.

    Attributes:
    w (h.Scalar): Width of the MiM capacitor in PDK Units (µm). Default is 1000 * MILLI.
    l (h.Scalar): Length of the MiM capacitor in PDK Units (µm). Default is 1000 * MILLI.
    mf (h.Scalar): Multiplier for the MiM capacitor. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    mf = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class Sky130VarParams:
    """
    A parameter class representing the varactor parameters for the Sky130 technology.
    These parameters include the width, length, and multiplier of the varactor device.

    Attributes:
    w (h.Scalar): Width of the varactor in PDK Units (µm). Default is 1000 * MILLI.
    l (h.Scalar): Length of the varactor in PDK Units (µm). Default is 1000 * MILLI.
    vm (h.Scalar): Multiplier for the varactor. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    vm = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


# FIXME: These params will not autoscale arguments, it doesn't really matter that they don't
# defaults are all that is really valid, but it'd be nice if an error could be thrown with
# parameters being provided or some kind of scaling in the class.
@h.paramclass
class Sky130VPPParams:
    """
    A parameter class representing the Vertical Parallel/Perpendicular Plate (VPP) capacitor parameters for the Sky130 technology.
    These parameters include the width, length, and multiplier of the VPP capacitor device.

    Attributes:
    w (h.Scalar): Width of the VPP capacitor in PDK Units (µm). Default is 1000 * MILLI.
    l (h.Scalar): Length of the VPP capacitor in PDK Units (µm). Default is 1000 * MILLI.
    mult (h.Scalar): Multiplier for the VPP capacitor. Default is 1.
    m (h.Scalar): Multiplier for the VPP capacitor (alias for mult). Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width in PDK Units (µm)", default=1000 * MILLI)
    l = h.Param(dtype=h.Scalar, desc="Length in PDK Units (µm)", default=1000 * MILLI)
    mult = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class Sky130DiodeParams:
    """
    A parameter class representing the diode parameters for the Sky130 technology.
    These parameters include the area and periphery junction capacitance of the diode device.

    Attributes:
    a (h.Scalar): Area of the diode in PDK Units (pm²). Default is 1 * TERA.
    pj (h.Scalar): Periphery junction capacitance of the diode in attofarads (aF). Default is 4 * MEGA.
    """

    area = h.Param(
        dtype=h.Scalar, desc="Area in PDK Units for Diodes (pm²)", default=1 * TERA
    )
    pj = h.Param(
        dtype=h.Scalar,
        desc="Periphery junction capacitance in aF (?)",
        default=4 * MEGA,
    )


@h.paramclass
class Sky130BipolarParams:
    """
    A parameter class representing the default bipolar transistor parameters for the Sky130 technology. These parameters include the multiplier for the bipolar transistor device.

    Attributes:
    m (h.Scalar): Multiplier for the bipolar transistor. Default is 1.
    """

    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class Sky130LogicParams:
    """
    A parameter class representing the default attributes of a logic gate cell

    Attributes:
    m (h.Scalar): Multiplier for logic circuits. Default is 1.
    """

    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


"""
This subsection of code defines a set of module creator functions for various electronic components in the Sky130 technology.
Each function is designed to create instances of external modules with the appropriate props and parameter types
for the specified component.

#! An important note is that `ExternalModule` props is used here to specify the spice prefix for the component used in
#! in different simulators. The introduction of props into the `ExternalModule` class is more generic than this, but this
#! is how we are using it for now. Future work will likely expand on this to make it more general.
"""

Mos5TPortList = [
    h.Port(name="g", desc="Gate"),
    h.Port(name="d", desc="Drain"),
    h.Port(name="s", desc="Source"),
    h.Port(name="b", desc="Bulk"),
    h.Port(name="sub", desc="Substrate"),
]


def _xtor_module(
    modname: str,
    params: h.Param = Sky130MosParams,
    num_terminals: int = 4,
) -> h.ExternalModule:

    """Transistor module creator, with module-name `name`.
    If `MoKey` `key` is provided, adds an entry in the `xtors` dictionary."""

    num2device = {4: h.Mos.port_list, 5: Mos5TPortList}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Mos {modname}",
        port_list=deepcopy(num2device[num_terminals]),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )

    return mod


def _res_module(
    modname: str,
    numterminals: int,
    params: h.Param,
    spicetype=SpiceType.SUBCKT,
) -> h.ExternalModule:

    """Resistor Module creator"""

    num2device = {2: PhysicalResistor, 3: ThreeTerminalResistor}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Res{numterminals} {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=params,
        spicetype=spicetype,
    )

    return mod


def _diode_module(
    modname: str,
) -> h.ExternalModule:

    """Diode Module creator"""

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Diode {modname}",
        port_list=deepcopy(Diode.port_list),
        paramtype=Sky130DiodeParams,
        spicetype=SpiceType.DIODE,
    )

    return mod


BJT4TPortList = [
    h.Port(name="c", desc="Collector"),
    h.Port(name="b", desc="Base"),
    h.Port(name="e", desc="Emitter"),
    h.Port(name="s", desc="Substrate"),
]


def _bjt_module(
    modname: str,
    numterminals: int = 3,
) -> h.ExternalModule:

    num2device = {3: Bipolar.port_list, 4: BJT4TPortList}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK BJT {modname}",
        port_list=deepcopy(num2device[numterminals]),
        paramtype=Sky130BipolarParams,
    )

    return mod


def _cap_module(
    modname: str,
    numterminals: int,
    params: h.Param,
) -> h.ExternalModule:

    num2device = {2: PhysicalCapacitor, 3: ThreeTerminalCapacitor}

    """Capacitor Module creator"""
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Cap{numterminals} {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=params,
    )

    return mod


PerpVPPPorts = [
    h.Port(name="p"),
    h.Port(name="n"),
    h.Port(name="t", desc="Top Shield"),
    h.Port(name="b", desc="Bottom Shield"),
]


def _vpp_module(
    modname: str,
    num_terminals: int,
) -> h.ExternalModule:
    """VPP Creator module"""

    if num_terminals == 3:

        mod = h.ExternalModule(
            domain=PDK_NAME,
            name=modname,
            desc=f"{PDK_NAME} PDK Parallel VPP {num_terminals} {modname}",
            port_list=deepcopy(h.primitives.ThreeTerminalPorts),
            paramtype=Sky130VPPParams,
        )

    elif num_terminals == 4:

        mod = h.ExternalModule(
            domain=PDK_NAME,
            name=modname,
            desc=f"{PDK_NAME} PDK Perpendicular VPP {modname}",
            port_list=deepcopy(PerpVPPPorts),
            paramtype=Sky130VPPParams,
        )

    return mod


def _logic_module(
    modname: str,
    family: str,
    terminals: List[str],
) -> h.ExternalModule:

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{family} {modname} Logic Circuit",
        port_list=[h.Port(name=i) for i in terminals],
        paramtype=Sky130LogicParams,
    )

    return mod


# Individuate component types
MosKey = Tuple[str, MosType, MosVth, MosFamily]

"""
These dictionaries are used to map all of the devices of the Sky130 technology
to their corresponding caller functions above. Keys and names are used to 
differentiate individual components and populate a namespace which can be used
to find and determine the correct internal device to use.
"""

xtors: Dict[MosKey, h.ExternalModule] = {
    # Add all generic transistors
    ("NMOS_1p8V_STD", MosType.NMOS, MosVth.STD, MosFamily.CORE): _xtor_module(
        "sky130_fd_pr__nfet_01v8"
    ),
    ("NMOS_1p8V_LOW", MosType.NMOS, MosVth.LOW, MosFamily.CORE): _xtor_module(
        "sky130_fd_pr__nfet_01v8_lvt"
    ),
    ("PMOS_1p8V_STD", MosType.PMOS, MosVth.STD, MosFamily.CORE): _xtor_module(
        "sky130_fd_pr__pfet_01v8"
    ),
    ("PMOS_1p8V_HIGH", MosType.PMOS, MosVth.HIGH, MosFamily.CORE): _xtor_module(
        "sky130_fd_pr__pfet_01v8_hvt"
    ),
    ("PMOS_1p8V_LOW", MosType.PMOS, MosVth.LOW, MosFamily.CORE): _xtor_module(
        "sky130_fd_pr__pfet_01v8_lvt"
    ),
    ("PMOS_5p5V_D10_STD", MosType.PMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__pfet_g5v0d10v5"
    ),
    ("NMOS_5p5V_D10_STD", MosType.NMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__nfet_g5v0d10v5"
    ),
    ("PMOS_5p5V_D16_STD", MosType.PMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__pfet_g5v0d16v0"
    ),
    ("NMOS_20p0V_STD", MosType.NMOS, MosVth.STD, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0", params=Sky130Mos20VParams
    ),
    ("NMOS_20p0V_LOW", MosType.NMOS, MosVth.ZERO, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0_zvt", params=Sky130Mos20VParams
    ),
    ("NMOS_ISO_20p0V", MosType.NMOS, MosVth.STD, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0_iso", params=Sky130Mos20VParams, num_terminals=5
    ),
    ("PMOS_20p0V", MosType.PMOS, MosVth.STD, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__pfet_20v0", params=Sky130Mos20VParams
    ),
    # Note there are no NMOS HVT!
    # Add Native FET entries
    ("NMOS_3p3V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_03v3_nvt"
    ),
    ("NMOS_5p0V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_05v0_nvt"
    ),
    ("NMOS_20p0V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): _xtor_module(
        "sky130_fd_pr__nfet_20v0_nvt", params=Sky130Mos20VParams
    ),
    # Add ESD FET entries
    ("ESD_NMOS_1p8V", MosType.NMOS, MosVth.STD, MosFamily.CORE): _xtor_module(
        "sky130_fd_pr__esd_nfet_01v8"
    ),
    ("ESD_NMOS_5p5V_D10", MosType.NMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__esd_nfet_g5v0d10v5"
    ),
    ("ESD_NMOS_5p5V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__esd_nfet_g5v0d10v5_nvt"
    ),
    ("ESD_PMOS_5p5V", MosType.PMOS, MosVth.STD, MosFamily.IO): _xtor_module(
        "sky130_fd_pr__esd_pfet_g5v0d10v5"
    ),
}

ress: Dict[str, h.ExternalModule] = {
    # 2-terminal generic resistors
    "GEN_PO": _res_module(
        "sky130_fd_pr__res_generic_po",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_L1": _res_module(
        "sky130_fd_pr__res_generic_l1",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M1": _res_module(
        "sky130_fd_pr__res_generic_m1",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M2": _res_module(
        "sky130_fd_pr__res_generic_m2",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M3": _res_module(
        "sky130_fd_pr__res_generic_m3",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M4": _res_module(
        "sky130_fd_pr__res_generic_m4",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M5": _res_module(
        "sky130_fd_pr__res_generic_m5",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    # 3-terminal generic resistors
    "GEN_ND": _res_module("sky130_fd_pr__res_generic_nd", 3, Sky130GenResParams),
    "GEN_PD": _res_module("sky130_fd_pr__res_generic_pd", 3, Sky130GenResParams),
    "GEN_ISO_PW": _res_module(
        "sky130_fd_pr__res_iso_pw",
        3,
        Sky130GenResParams,
    ),
    # 3-terminal precision resistors
    "PP_PREC_0p35": _res_module(
        "sky130_fd_pr__res_high_po_0p35", 3, Sky130PrecResParams
    ),
    "PP_PREC_0p69": _res_module(
        "sky130_fd_pr__res_high_po_0p69", 3, Sky130PrecResParams
    ),
    "PP_PREC_1p41": _res_module(
        "sky130_fd_pr__res_high_po_1p41", 3, Sky130PrecResParams
    ),
    "PP_PREC_2p85": _res_module(
        "sky130_fd_pr__res_high_po_2p85", 3, Sky130PrecResParams
    ),
    "PP_PREC_5p73": _res_module(
        "sky130_fd_pr__res_high_po_5p73", 3, Sky130PrecResParams
    ),
    "PM_PREC_0p35": _res_module(
        "sky130_fd_pr__res_xhigh_po_0p35", 3, Sky130PrecResParams
    ),
    "PM_PREC_0p69": _res_module(
        "sky130_fd_pr__res_xhigh_po_0p69", 3, Sky130PrecResParams
    ),
    "PM_PREC_1p41": _res_module(
        "sky130_fd_pr__res_xhigh_po_1p41", 3, Sky130PrecResParams
    ),
    "PM_PREC_2p85": _res_module(
        "sky130_fd_pr__res_xhigh_po_2p85", 3, Sky130PrecResParams
    ),
    "PM_PREC_5p73": _res_module(
        "sky130_fd_pr__res_xhigh_po_5p73", 3, Sky130PrecResParams
    ),
}

diodes: Dict[str, h.ExternalModule] = {
    # Add diodes
    "PWND_5p5V": _diode_module("sky130_fd_pr__diode_pw2nd_05v5"),
    "PWND_11p0V": _diode_module("sky130_fd_pr__diode_pw2nd_11v0"),
    "PWND_5p5V_NAT": _diode_module("sky130_fd_pr__diode_pw2nd_05v5_nvt"),
    "PWND_5p5V_LVT": _diode_module("sky130_fd_pr__diode_pw2nd_05v5_lvt"),
    "PDNW_5p5V": _diode_module("sky130_fd_pr__diode_pd2nw_05v5"),
    "PDNW_11p0V": _diode_module("sky130_fd_pr__diode_pd2nw_11v0"),
    "PDNW_5p5V_HVT": _diode_module("sky130_fd_pr__diode_pd2nw_05v5_hvt"),
    "PDNW_5p5V_LVT": _diode_module("sky130_fd_pr__diode_pd2nw_05v5_lvt"),
    "PX_RF_PSNW": _diode_module("sky130_fd_pr__model__parasitic__rf_diode_ps2nw"),
    "PX_RF_PWDN": _diode_module("sky130_fd_pr__model__parasitic__rf_diode_pw2dn"),
    "PX_PWDN": _diode_module("sky130_fd_pr__model__parasitic__diode_pw2dn"),
    "PX_PSDN": _diode_module("sky130_fd_pr__model__parasitic__diode_ps2dn"),
    "PX_PSNW": _diode_module("sky130_fd_pr__model__parasitic__diode_ps2nw"),
}

"""
BJTs in this PDK are all subcircuits but are distributed in a way that is quite unusual
and can make it particularly difficult to access them without a PR to the PDK itself.

As noted here there is no functional difference between rf and non-rf BJTs in SKY130:

https://open-source-silicon.slack.com/archives/C016HUV935L/p1650549447460139?thread_ts=1650545374.248099&cid=C016HUV935L
"""
bjts: Dict[str, h.ExternalModule] = {
    # Add BJTs
    "NPN_5p0V_1x2": _bjt_module("sky130_fd_pr__npn_05v5_W1p00L2p00", numterminals=4),
    "NPN_11p0V_1x1": _bjt_module("sky130_fd_pr__npn_11v0_W1p00L1p00", numterminals=4),
    "NPN_5p0V_1x1": _bjt_module("sky130_fd_pr__npn_05v5_W1p00L1p00", numterminals=4),
    "PNP_5p0V_0p68x0p68": _bjt_module("sky130_fd_pr__pnp_05v5_W0p68L0p68"),
    "PNP_5p0V_3p40x3p40": _bjt_module("sky130_fd_pr__pnp_05v5_W3p40L3p40"),
}

caps: Dict[str, h.ExternalModule] = {
    # List all MiM capacitors
    # https://open-source-silicon.slack.com/archives/C016HUV935L/p1618923323152300?thread_ts=1618887703.151600&cid=C016HUV935L
    "MIM_M3": _cap_module(
        "sky130_fd_pr__cap_mim_m3_1",
        numterminals=2,
        params=Sky130MimParams,
    ),
    "MIM_M4": _cap_module(
        "sky130_fd_pr__cap_mim_m3_2",
        numterminals=2,
        params=Sky130MimParams,
    ),
    # List available Varactors
    "VAR_LVT": _cap_module(
        "sky130_fd_pr__cap_var_lvt",
        numterminals=3,
        params=Sky130VarParams,
    ),
    "VAR_HVT": _cap_module(
        "sky130_fd_pr__cap_var_hvt",
        numterminals=3,
        params=Sky130VarParams,
    ),
}

vpps: Dict[str, h.ExternalModule] = {
    # List Parallel VPP capacitors
    "VPP_PARA_1": _vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2", 3),
    "VPP_PARA_2": _vpp_module("sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield", 3),
    "VPP_PARA_3": _vpp_module("sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_noshield", 3),
    "VPP_PARA_4": _vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield", 3),
    "VPP_PARA_5": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_noshield", 3),
    "VPP_PARA_6": _vpp_module(
        "sky130_fd_pr__cap_vpp_44p7x23p1_pol1m1m2m3m4m5_noshield", 3
    ),
    "VPP_PARA_7": _vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x06p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    "VPP_PARA_8": _vpp_module(
        "sky130_fd_pr__cap_vpp_02p9x06p1_m1m2m3m4_shieldl1_fingercap2", 3
    ),
    "VPP_PARA_9": _vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x11p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    "VPP_PARA_10": _vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x21p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    "VPP_PARA_11": _vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x41p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    # List Perpendicular VPP capacitors
    "VPP_PERP_1": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5", 4),
    "VPP_PERP_2": _vpp_module(
        "sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5", 4
    ),
    "VPP_PERP_3": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3m4_shieldl1m5", 4),
    "VPP_PERP_4": _vpp_module(
        "sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1m5_floatm4", 4
    ),
    "VPP_PERP_5": _vpp_module(
        "sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1m5_floatm4", 4
    ),
    "VPP_PERP_6": _vpp_module(
        "sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1m5_floatm4", 4
    ),
    "VPP_PERP_7": _vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3_shieldm4", 4),
    "VPP_PERP_8": _vpp_module("sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2m3_shieldpom4", 4),
    "VPP_PERP_9": _vpp_module("sky130_fd_pr__cap_vpp_06p8x06p1_m1m2m3_shieldl1m4", 4),
    "VPP_PERP_10": _vpp_module(
        "sky130_fd_pr__cap_vpp_11p3x11p8_l1m1m2m3m4_shieldm5_nhvtop", 4
    ),
}

# Collected `ExternalModule`s are stored in the `modules` namespace
modules = SimpleNamespace()

# Add each to the `modules` namespace
for name, mod in xtors.items():
    setattr(modules, name[0], mod)
for name, mod in ress.items():
    setattr(modules, name, mod)
for name, mod in caps.items():
    setattr(modules, name, mod)
for name, mod in diodes.items():
    setattr(modules, name, mod)
for name, mod in bjts.items():
    setattr(modules, name, mod)
for name, mod in vpps.items():
    setattr(modules, name, mod)


@dataclass
class Cache:
    """# Module-Scope Cache(s)"""

    mos_modcalls: Dict[MosParams, h.ExternalModuleCall] = field(default_factory=dict)

    res_modcalls: Dict[PhysicalResistorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )

    cap_modcalls: Dict[PhysicalCapacitorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )

    diode_modcalls: Dict[DiodeParams, h.ExternalModule] = field(default_factory=dict)

    bjt_modcalls: Dict[BipolarParams, h.ExternalModule] = field(default_factory=dict)


CACHE = Cache()

"""
This section of code defines default sizes for various electronic components in the Sky130 technology,
including transistors, resistors, and capacitors. Default dimensions are provided in microns or PDK units,
with the sizes stored in dictionaries: default_xtor_size for transistors, default_gen_res_size for generic resistors,
default_prec_res_L for precise resistors, and default_cap_sizes for capacitors.
These default sizes are important for creating instances of the components with proper dimensions,
ensuring correct layout and performance in the circuit designs.
"""

# Default param dicts
default_xtor_size = {
    "sky130_fd_pr__nfet_01v8": (h.Scalar(inner=0.420 * µ), h.Scalar(inner=0.150 * µ)),
    "sky130_fd_pr__nfet_01v8_lvt": (
        h.Scalar(inner=0.420 * µ),
        h.Scalar(inner=0.150 * µ),
    ),
    "sky130_fd_pr__pfet_01v8": (h.Scalar(inner=0.550 * µ), h.Scalar(inner=0.150 * µ)),
    "sky130_fd_pr__pfet_01v8_hvt": (
        h.Scalar(inner=0.550 * µ),
        h.Scalar(inner=0.150 * µ),
    ),
    "sky130_fd_pr__pfet_01v8_lvt": (
        h.Scalar(inner=0.550 * µ),
        h.Scalar(inner=0.350 * µ),
    ),
    "sky130_fd_pr__pfet_g5v0d10v5": (
        h.Scalar(inner=0.420 * µ),
        h.Scalar(inner=0.500 * µ),
    ),
    "sky130_fd_pr__nfet_g5v0d10v5": (
        h.Scalar(inner=0.420 * µ),
        h.Scalar(inner=0.500 * µ),
    ),
    "sky130_fd_pr__pfet_g5v0d16v0": (
        h.Scalar(inner=5.000 * µ),
        h.Scalar(inner=0.660 * µ),
    ),
    "sky130_fd_pr__nfet_20v0": (h.Scalar(inner=29.410 * µ), h.Scalar(inner=2.950 * µ)),
    "sky130_fd_pr__nfet_20v0_zvt": (
        h.Scalar(inner=30.000 * µ),
        h.Scalar(inner=1.500 * µ),
    ),
    "sky130_fd_pr__nfet_20v0_iso": (
        h.Scalar(inner=30.000 * µ),
        h.Scalar(inner=1.500 * µ),
    ),
    "sky130_fd_pr__pfet_20v0": (h.Scalar(inner=30.000 * µ), h.Scalar(inner=1.000 * µ)),
    "sky130_fd_pr__nfet_03v3_nvt": (
        h.Scalar(inner=0.700 * µ),
        h.Scalar(inner=0.500 * µ),
    ),
    "sky130_fd_pr__nfet_05v0_nvt": (
        h.Scalar(inner=0.700 * µ),
        h.Scalar(inner=0.900 * µ),
    ),
    "sky130_fd_pr__nfet_20v0_nvt": (
        h.Scalar(inner=30.000 * µ),
        h.Scalar(inner=1.000 * µ),
    ),
    "sky130_fd_pr__esd_nfet_01v8": (
        h.Scalar(inner=20.350 * µ),
        h.Scalar(inner=0.165 * µ),
    ),
    "sky130_fd_pr__esd_nfet_g5v0d10v5": (
        h.Scalar(inner=14.500 * µ),
        h.Scalar(inner=0.550 * µ),
    ),
    "sky130_fd_pr__esd_nfet_g5v0d10v5_nvt": (
        h.Scalar(inner=10.000 * µ),
        h.Scalar(inner=0.900 * µ),
    ),
    "sky130_fd_pr__esd_pfet_g5v0d10v5": (
        h.Scalar(inner=14.500 * µ),
        h.Scalar(inner=0.550 * µ),
    ),
}

default_gen_res_size = {
    "sky130_fd_pr__res_generic_po": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_l1": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_m1": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_m2": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_m3": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_m4": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_m5": (
        h.Scalar(inner=0.720 * µ),
        h.Scalar(inner=0.290 * µ),
    ),
    "sky130_fd_pr__res_generic_nd": (
        h.Scalar(inner=0.150 * µ),
        h.Scalar(inner=0.270 * µ),
    ),
    "sky130_fd_pr__res_generic_pd": (
        h.Scalar(inner=0.150 * µ),
        h.Scalar(inner=0.270 * µ),
    ),
    # FIXME: This value is lifted from xschem but can't be found in documentation
    "sky130_fd_pr__res_iso_pw": (h.Scalar(inner=2.650 * µ), h.Scalar(inner=2.650 * µ)),
}

# These have to be left in microns for parsing reasons
default_prec_res_L = {
    "sky130_fd_pr__res_high_po_0p35": h.Scalar(inner=0.350),
    "sky130_fd_pr__res_high_po_0p69": h.Scalar(inner=0.690),
    "sky130_fd_pr__res_high_po_1p41": h.Scalar(inner=1.410),
    "sky130_fd_pr__res_high_po_2p85": h.Scalar(inner=2.850),
    "sky130_fd_pr__res_high_po_5p73": h.Scalar(inner=5.300),
    "sky130_fd_pr__res_xhigh_po_0p35": h.Scalar(inner=0.350),
    "sky130_fd_pr__res_xhigh_po_0p69": h.Scalar(inner=0.690),
    "sky130_fd_pr__res_xhigh_po_1p41": h.Scalar(inner=1.410),
    "sky130_fd_pr__res_xhigh_po_2p85": h.Scalar(inner=2.850),
    "sky130_fd_pr__res_xhigh_po_5p73": h.Scalar(inner=5.300),
}

default_cap_sizes = {
    # FIXME: Using documentation minimum sizing not sure of correct answer
    "sky130_fd_pr__cap_mim_m3_1": (
        h.Scalar(inner=2.000 * µ),
        h.Scalar(inner=2.000 * µ),
    ),
    "sky130_fd_pr__cap_mim_m3_2": (
        h.Scalar(inner=2.000 * µ),
        h.Scalar(inner=2.000 * µ),
    ),
    "sky130_fd_pr__cap_var_lvt": (h.Scalar(inner=0.180 * µ), h.Scalar(inner=0.180 * µ)),
    "sky130_fd_pr__cap_var_hvt": (h.Scalar(inner=0.180 * µ), h.Scalar(inner=0.180 * µ)),
}
