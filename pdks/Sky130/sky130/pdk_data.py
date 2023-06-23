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

hd: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_hd__a2bb2o_1": _logic_module(
        "sky130_fd_sc_hd__a2bb2o_1",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a2bb2o_2": _logic_module(
        "sky130_fd_sc_hd__a2bb2o_2",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a2bb2o_4": _logic_module(
        "sky130_fd_sc_hd__a2bb2o_4",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a2bb2oi_1": _logic_module(
        "sky130_fd_sc_hd__a2bb2oi_1",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a2bb2oi_2": _logic_module(
        "sky130_fd_sc_hd__a2bb2oi_2",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a2bb2oi_4": _logic_module(
        "sky130_fd_sc_hd__a2bb2oi_4",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21bo_1": _logic_module(
        "sky130_fd_sc_hd__a21bo_1",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a21bo_2": _logic_module(
        "sky130_fd_sc_hd__a21bo_2",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a21bo_4": _logic_module(
        "sky130_fd_sc_hd__a21bo_4",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a21boi_0": _logic_module(
        "sky130_fd_sc_hd__a21boi_0",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21boi_1": _logic_module(
        "sky130_fd_sc_hd__a21boi_1",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21boi_2": _logic_module(
        "sky130_fd_sc_hd__a21boi_2",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21boi_4": _logic_module(
        "sky130_fd_sc_hd__a21boi_4",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21o_1": _logic_module(
        "sky130_fd_sc_hd__a21o_1",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a21o_2": _logic_module(
        "sky130_fd_sc_hd__a21o_2",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a21o_4": _logic_module(
        "sky130_fd_sc_hd__a21o_4",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a21oi_1": _logic_module(
        "sky130_fd_sc_hd__a21oi_1",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21oi_2": _logic_module(
        "sky130_fd_sc_hd__a21oi_2",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a21oi_4": _logic_module(
        "sky130_fd_sc_hd__a21oi_4",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a22o_1": _logic_module(
        "sky130_fd_sc_hd__a22o_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a22o_2": _logic_module(
        "sky130_fd_sc_hd__a22o_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a22o_4": _logic_module(
        "sky130_fd_sc_hd__a22o_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a22oi_1": _logic_module(
        "sky130_fd_sc_hd__a22oi_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a22oi_2": _logic_module(
        "sky130_fd_sc_hd__a22oi_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a22oi_4": _logic_module(
        "sky130_fd_sc_hd__a22oi_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a31o_1": _logic_module(
        "sky130_fd_sc_hd__a31o_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a31o_2": _logic_module(
        "sky130_fd_sc_hd__a31o_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a31o_4": _logic_module(
        "sky130_fd_sc_hd__a31o_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a31oi_1": _logic_module(
        "sky130_fd_sc_hd__a31oi_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a31oi_2": _logic_module(
        "sky130_fd_sc_hd__a31oi_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a31oi_4": _logic_module(
        "sky130_fd_sc_hd__a31oi_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a32o_1": _logic_module(
        "sky130_fd_sc_hd__a32o_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a32o_2": _logic_module(
        "sky130_fd_sc_hd__a32o_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a32o_4": _logic_module(
        "sky130_fd_sc_hd__a32o_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a32oi_1": _logic_module(
        "sky130_fd_sc_hd__a32oi_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a32oi_2": _logic_module(
        "sky130_fd_sc_hd__a32oi_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a32oi_4": _logic_module(
        "sky130_fd_sc_hd__a32oi_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a41o_1": _logic_module(
        "sky130_fd_sc_hd__a41o_1",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a41o_2": _logic_module(
        "sky130_fd_sc_hd__a41o_2",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a41o_4": _logic_module(
        "sky130_fd_sc_hd__a41o_4",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a41oi_1": _logic_module(
        "sky130_fd_sc_hd__a41oi_1",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a41oi_2": _logic_module(
        "sky130_fd_sc_hd__a41oi_2",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a41oi_4": _logic_module(
        "sky130_fd_sc_hd__a41oi_4",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a211o_1": _logic_module(
        "sky130_fd_sc_hd__a211o_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a211o_2": _logic_module(
        "sky130_fd_sc_hd__a211o_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a211o_4": _logic_module(
        "sky130_fd_sc_hd__a211o_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a211oi_1": _logic_module(
        "sky130_fd_sc_hd__a211oi_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a211oi_2": _logic_module(
        "sky130_fd_sc_hd__a211oi_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a211oi_4": _logic_module(
        "sky130_fd_sc_hd__a211oi_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a221o_1": _logic_module(
        "sky130_fd_sc_hd__a221o_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a221o_2": _logic_module(
        "sky130_fd_sc_hd__a221o_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a221o_4": _logic_module(
        "sky130_fd_sc_hd__a221o_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a221oi_1": _logic_module(
        "sky130_fd_sc_hd__a221oi_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a221oi_2": _logic_module(
        "sky130_fd_sc_hd__a221oi_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a221oi_4": _logic_module(
        "sky130_fd_sc_hd__a221oi_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a222oi_1": _logic_module(
        "sky130_fd_sc_hd__a222oi_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a311o_1": _logic_module(
        "sky130_fd_sc_hd__a311o_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a311o_2": _logic_module(
        "sky130_fd_sc_hd__a311o_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a311o_4": _logic_module(
        "sky130_fd_sc_hd__a311o_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a311oi_1": _logic_module(
        "sky130_fd_sc_hd__a311oi_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a311oi_2": _logic_module(
        "sky130_fd_sc_hd__a311oi_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a311oi_4": _logic_module(
        "sky130_fd_sc_hd__a311oi_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a2111o_1": _logic_module(
        "sky130_fd_sc_hd__a2111o_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a2111o_2": _logic_module(
        "sky130_fd_sc_hd__a2111o_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a2111o_4": _logic_module(
        "sky130_fd_sc_hd__a2111o_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__a2111oi_0": _logic_module(
        "sky130_fd_sc_hd__a2111oi_0",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a2111oi_1": _logic_module(
        "sky130_fd_sc_hd__a2111oi_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a2111oi_2": _logic_module(
        "sky130_fd_sc_hd__a2111oi_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__a2111oi_4": _logic_module(
        "sky130_fd_sc_hd__a2111oi_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__and2_0": _logic_module(
        "sky130_fd_sc_hd__and2_0",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and2_1": _logic_module(
        "sky130_fd_sc_hd__and2_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and2_2": _logic_module(
        "sky130_fd_sc_hd__and2_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and2_4": _logic_module(
        "sky130_fd_sc_hd__and2_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and2b_1": _logic_module(
        "sky130_fd_sc_hd__and2b_1",
        "High Density",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and2b_2": _logic_module(
        "sky130_fd_sc_hd__and2b_2",
        "High Density",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and2b_4": _logic_module(
        "sky130_fd_sc_hd__and2b_4",
        "High Density",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and3_1": _logic_module(
        "sky130_fd_sc_hd__and3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and3_2": _logic_module(
        "sky130_fd_sc_hd__and3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and3_4": _logic_module(
        "sky130_fd_sc_hd__and3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and3b_1": _logic_module(
        "sky130_fd_sc_hd__and3b_1",
        "High Density",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and3b_2": _logic_module(
        "sky130_fd_sc_hd__and3b_2",
        "High Density",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and3b_4": _logic_module(
        "sky130_fd_sc_hd__and3b_4",
        "High Density",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4_1": _logic_module(
        "sky130_fd_sc_hd__and4_1",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4_2": _logic_module(
        "sky130_fd_sc_hd__and4_2",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4_4": _logic_module(
        "sky130_fd_sc_hd__and4_4",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4b_1": _logic_module(
        "sky130_fd_sc_hd__and4b_1",
        "High Density",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4b_2": _logic_module(
        "sky130_fd_sc_hd__and4b_2",
        "High Density",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4b_4": _logic_module(
        "sky130_fd_sc_hd__and4b_4",
        "High Density",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4bb_1": _logic_module(
        "sky130_fd_sc_hd__and4bb_1",
        "High Density",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4bb_2": _logic_module(
        "sky130_fd_sc_hd__and4bb_2",
        "High Density",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__and4bb_4": _logic_module(
        "sky130_fd_sc_hd__and4bb_4",
        "High Density",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_1": _logic_module(
        "sky130_fd_sc_hd__buf_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_2": _logic_module(
        "sky130_fd_sc_hd__buf_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_4": _logic_module(
        "sky130_fd_sc_hd__buf_4",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_6": _logic_module(
        "sky130_fd_sc_hd__buf_6",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_8": _logic_module(
        "sky130_fd_sc_hd__buf_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_12": _logic_module(
        "sky130_fd_sc_hd__buf_12",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__buf_16": _logic_module(
        "sky130_fd_sc_hd__buf_16",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__bufbuf_8": _logic_module(
        "sky130_fd_sc_hd__bufbuf_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__bufbuf_16": _logic_module(
        "sky130_fd_sc_hd__bufbuf_16",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__bufinv_8": _logic_module(
        "sky130_fd_sc_hd__bufinv_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__bufinv_16": _logic_module(
        "sky130_fd_sc_hd__bufinv_16",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkbuf_1": _logic_module(
        "sky130_fd_sc_hd__clkbuf_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkbuf_2": _logic_module(
        "sky130_fd_sc_hd__clkbuf_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkbuf_4": _logic_module(
        "sky130_fd_sc_hd__clkbuf_4",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkbuf_8": _logic_module(
        "sky130_fd_sc_hd__clkbuf_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkbuf_16": _logic_module(
        "sky130_fd_sc_hd__clkbuf_16",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s15_1": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s15_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s15_2": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s15_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s18_1": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s18_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s18_2": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s18_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s25_1": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s25_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s25_2": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s25_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s50_1": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s50_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkdlybuf4s50_2": _logic_module(
        "sky130_fd_sc_hd__clkdlybuf4s50_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__clkinv_1": _logic_module(
        "sky130_fd_sc_hd__clkinv_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkinv_2": _logic_module(
        "sky130_fd_sc_hd__clkinv_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkinv_4": _logic_module(
        "sky130_fd_sc_hd__clkinv_4",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkinv_8": _logic_module(
        "sky130_fd_sc_hd__clkinv_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkinv_16": _logic_module(
        "sky130_fd_sc_hd__clkinv_16",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkinvlp_2": _logic_module(
        "sky130_fd_sc_hd__clkinvlp_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__clkinvlp_4": _logic_module(
        "sky130_fd_sc_hd__clkinvlp_4",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__conb_1": _logic_module(
        "sky130_fd_sc_hd__conb_1",
        "High Density",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_hd__decap_3": _logic_module(
        "sky130_fd_sc_hd__decap_3", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__decap_4": _logic_module(
        "sky130_fd_sc_hd__decap_4", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__decap_6": _logic_module(
        "sky130_fd_sc_hd__decap_6", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__decap_8": _logic_module(
        "sky130_fd_sc_hd__decap_8", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__decap_12": _logic_module(
        "sky130_fd_sc_hd__decap_12", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__dfbbn_1": _logic_module(
        "sky130_fd_sc_hd__dfbbn_1",
        "High Density",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfbbn_2": _logic_module(
        "sky130_fd_sc_hd__dfbbn_2",
        "High Density",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfbbp_1": _logic_module(
        "sky130_fd_sc_hd__dfbbp_1",
        "High Density",
        ["CLK", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfrbp_1": _logic_module(
        "sky130_fd_sc_hd__dfrbp_1",
        "High Density",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfrbp_2": _logic_module(
        "sky130_fd_sc_hd__dfrbp_2",
        "High Density",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfrtn_1": _logic_module(
        "sky130_fd_sc_hd__dfrtn_1",
        "High Density",
        ["CLK_N", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfrtp_1": _logic_module(
        "sky130_fd_sc_hd__dfrtp_1",
        "High Density",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfrtp_2": _logic_module(
        "sky130_fd_sc_hd__dfrtp_2",
        "High Density",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfrtp_4": _logic_module(
        "sky130_fd_sc_hd__dfrtp_4",
        "High Density",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfsbp_1": _logic_module(
        "sky130_fd_sc_hd__dfsbp_1",
        "High Density",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfsbp_2": _logic_module(
        "sky130_fd_sc_hd__dfsbp_2",
        "High Density",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfstp_1": _logic_module(
        "sky130_fd_sc_hd__dfstp_1",
        "High Density",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfstp_2": _logic_module(
        "sky130_fd_sc_hd__dfstp_2",
        "High Density",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfstp_4": _logic_module(
        "sky130_fd_sc_hd__dfstp_4",
        "High Density",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfxbp_1": _logic_module(
        "sky130_fd_sc_hd__dfxbp_1",
        "High Density",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfxbp_2": _logic_module(
        "sky130_fd_sc_hd__dfxbp_2",
        "High Density",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dfxtp_1": _logic_module(
        "sky130_fd_sc_hd__dfxtp_1",
        "High Density",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfxtp_2": _logic_module(
        "sky130_fd_sc_hd__dfxtp_2",
        "High Density",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dfxtp_4": _logic_module(
        "sky130_fd_sc_hd__dfxtp_4",
        "High Density",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__diode_2": _logic_module(
        "sky130_fd_sc_hd__diode_2",
        "High Density",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__dlclkp_1": _logic_module(
        "sky130_fd_sc_hd__dlclkp_1",
        "High Density",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hd__dlclkp_2": _logic_module(
        "sky130_fd_sc_hd__dlclkp_2",
        "High Density",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hd__dlclkp_4": _logic_module(
        "sky130_fd_sc_hd__dlclkp_4",
        "High Density",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hd__dlrbn_1": _logic_module(
        "sky130_fd_sc_hd__dlrbn_1",
        "High Density",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlrbn_2": _logic_module(
        "sky130_fd_sc_hd__dlrbn_2",
        "High Density",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlrbp_1": _logic_module(
        "sky130_fd_sc_hd__dlrbp_1",
        "High Density",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlrbp_2": _logic_module(
        "sky130_fd_sc_hd__dlrbp_2",
        "High Density",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlrtn_1": _logic_module(
        "sky130_fd_sc_hd__dlrtn_1",
        "High Density",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlrtn_2": _logic_module(
        "sky130_fd_sc_hd__dlrtn_2",
        "High Density",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlrtn_4": _logic_module(
        "sky130_fd_sc_hd__dlrtn_4",
        "High Density",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlrtp_1": _logic_module(
        "sky130_fd_sc_hd__dlrtp_1",
        "High Density",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlrtp_2": _logic_module(
        "sky130_fd_sc_hd__dlrtp_2",
        "High Density",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlrtp_4": _logic_module(
        "sky130_fd_sc_hd__dlrtp_4",
        "High Density",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlxbn_1": _logic_module(
        "sky130_fd_sc_hd__dlxbn_1",
        "High Density",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlxbn_2": _logic_module(
        "sky130_fd_sc_hd__dlxbn_2",
        "High Density",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlxbp_1": _logic_module(
        "sky130_fd_sc_hd__dlxbp_1",
        "High Density",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__dlxtn_1": _logic_module(
        "sky130_fd_sc_hd__dlxtn_1",
        "High Density",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlxtn_2": _logic_module(
        "sky130_fd_sc_hd__dlxtn_2",
        "High Density",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlxtn_4": _logic_module(
        "sky130_fd_sc_hd__dlxtn_4",
        "High Density",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlxtp_1": _logic_module(
        "sky130_fd_sc_hd__dlxtp_1",
        "High Density",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__dlygate4sd1_1": _logic_module(
        "sky130_fd_sc_hd__dlygate4sd1_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__dlygate4sd2_1": _logic_module(
        "sky130_fd_sc_hd__dlygate4sd2_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__dlygate4sd3_1": _logic_module(
        "sky130_fd_sc_hd__dlygate4sd3_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__dlymetal6s2s_1": _logic_module(
        "sky130_fd_sc_hd__dlymetal6s2s_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__dlymetal6s4s_1": _logic_module(
        "sky130_fd_sc_hd__dlymetal6s4s_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__dlymetal6s6s_1": _logic_module(
        "sky130_fd_sc_hd__dlymetal6s6s_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__ebufn_1": _logic_module(
        "sky130_fd_sc_hd__ebufn_1",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__ebufn_2": _logic_module(
        "sky130_fd_sc_hd__ebufn_2",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__ebufn_4": _logic_module(
        "sky130_fd_sc_hd__ebufn_4",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__ebufn_8": _logic_module(
        "sky130_fd_sc_hd__ebufn_8",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__edfxbp_1": _logic_module(
        "sky130_fd_sc_hd__edfxbp_1",
        "High Density",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__edfxtp_1": _logic_module(
        "sky130_fd_sc_hd__edfxtp_1",
        "High Density",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__einvn_0": _logic_module(
        "sky130_fd_sc_hd__einvn_0",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvn_1": _logic_module(
        "sky130_fd_sc_hd__einvn_1",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvn_2": _logic_module(
        "sky130_fd_sc_hd__einvn_2",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvn_4": _logic_module(
        "sky130_fd_sc_hd__einvn_4",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvn_8": _logic_module(
        "sky130_fd_sc_hd__einvn_8",
        "High Density",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvp_1": _logic_module(
        "sky130_fd_sc_hd__einvp_1",
        "High Density",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvp_2": _logic_module(
        "sky130_fd_sc_hd__einvp_2",
        "High Density",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvp_4": _logic_module(
        "sky130_fd_sc_hd__einvp_4",
        "High Density",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__einvp_8": _logic_module(
        "sky130_fd_sc_hd__einvp_8",
        "High Density",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hd__fa_1": _logic_module(
        "sky130_fd_sc_hd__fa_1",
        "High Density",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__fa_2": _logic_module(
        "sky130_fd_sc_hd__fa_2",
        "High Density",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__fa_4": _logic_module(
        "sky130_fd_sc_hd__fa_4",
        "High Density",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__fah_1": _logic_module(
        "sky130_fd_sc_hd__fah_1",
        "High Density",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__fahcin_1": _logic_module(
        "sky130_fd_sc_hd__fahcin_1",
        "High Density",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__fahcon_1": _logic_module(
        "sky130_fd_sc_hd__fahcon_1",
        "High Density",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT_N", "SUM"],
    ),
    "sky130_fd_sc_hd__fill_1": _logic_module(
        "sky130_fd_sc_hd__fill_1", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__fill_2": _logic_module(
        "sky130_fd_sc_hd__fill_2", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__fill_4": _logic_module(
        "sky130_fd_sc_hd__fill_4", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__fill_8": _logic_module(
        "sky130_fd_sc_hd__fill_8", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__ha_1": _logic_module(
        "sky130_fd_sc_hd__ha_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__ha_2": _logic_module(
        "sky130_fd_sc_hd__ha_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__ha_4": _logic_module(
        "sky130_fd_sc_hd__ha_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hd__inv_1": _logic_module(
        "sky130_fd_sc_hd__inv_1",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__inv_2": _logic_module(
        "sky130_fd_sc_hd__inv_2",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__inv_4": _logic_module(
        "sky130_fd_sc_hd__inv_4",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__inv_6": _logic_module(
        "sky130_fd_sc_hd__inv_6",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__inv_8": _logic_module(
        "sky130_fd_sc_hd__inv_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__inv_12": _logic_module(
        "sky130_fd_sc_hd__inv_12",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__inv_16": _logic_module(
        "sky130_fd_sc_hd__inv_16",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__lpflow_bleeder_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_bleeder_1",
        "High Density",
        ["SHORT", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_clkbufkapwr_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkbufkapwr_1",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_clkbufkapwr_2": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkbufkapwr_2",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_clkbufkapwr_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkbufkapwr_4",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_clkbufkapwr_8": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkbufkapwr_8",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_clkbufkapwr_16": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkbufkapwr_16",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_clkinvkapwr_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkinvkapwr_1",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__lpflow_clkinvkapwr_2": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkinvkapwr_2",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__lpflow_clkinvkapwr_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkinvkapwr_4",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__lpflow_clkinvkapwr_8": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkinvkapwr_8",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__lpflow_clkinvkapwr_16": _logic_module(
        "sky130_fd_sc_hd__lpflow_clkinvkapwr_16",
        "High Density",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__lpflow_decapkapwr_3": _logic_module(
        "sky130_fd_sc_hd__lpflow_decapkapwr_3",
        "High Density",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_decapkapwr_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_decapkapwr_4",
        "High Density",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_decapkapwr_6": _logic_module(
        "sky130_fd_sc_hd__lpflow_decapkapwr_6",
        "High Density",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_decapkapwr_8": _logic_module(
        "sky130_fd_sc_hd__lpflow_decapkapwr_8",
        "High Density",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_decapkapwr_12": _logic_module(
        "sky130_fd_sc_hd__lpflow_decapkapwr_12",
        "High Density",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_inputiso0n_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_inputiso0n_1",
        "High Density",
        ["A", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_inputiso0p_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_inputiso0p_1",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_inputiso1n_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_inputiso1n_1",
        "High Density",
        ["A", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_inputiso1p_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_inputiso1p_1",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_inputisolatch_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_inputisolatch_1",
        "High Density",
        ["D", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__lpflow_isobufsrc_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_isobufsrc_1",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_isobufsrc_2": _logic_module(
        "sky130_fd_sc_hd__lpflow_isobufsrc_2",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_isobufsrc_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_isobufsrc_4",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_isobufsrc_8": _logic_module(
        "sky130_fd_sc_hd__lpflow_isobufsrc_8",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_isobufsrc_16": _logic_module(
        "sky130_fd_sc_hd__lpflow_isobufsrc_16",
        "High Density",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_isobufsrckapwr_16": _logic_module(
        "sky130_fd_sc_hd__lpflow_isobufsrckapwr_16",
        "High Density",
        ["A", "SLEEP", "KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_1",
        "High Density",
        ["A", "VGND", "VPB", "VPWRIN", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_2": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_2",
        "High Density",
        ["A", "VGND", "VPB", "VPWRIN", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_4",
        "High Density",
        ["A", "VGND", "VPB", "VPWRIN", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_4",
        "High Density",
        ["A", "LOWLVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_1": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_1",
        "High Density",
        ["A", "LOWLVPWR", "VGND", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_2": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_2",
        "High Density",
        ["A", "LOWLVPWR", "VGND", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_4": _logic_module(
        "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_4",
        "High Density",
        ["A", "LOWLVPWR", "VGND", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__macro_sparecell": _logic_module(
        "sky130_fd_sc_hd__macro_sparecell",
        "High Density",
        ["VGND", "VNB", "VPB", "VPWR", "LO"],
    ),
    "sky130_fd_sc_hd__maj3_1": _logic_module(
        "sky130_fd_sc_hd__maj3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__maj3_2": _logic_module(
        "sky130_fd_sc_hd__maj3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__maj3_4": _logic_module(
        "sky130_fd_sc_hd__maj3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux2_1": _logic_module(
        "sky130_fd_sc_hd__mux2_1",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux2_2": _logic_module(
        "sky130_fd_sc_hd__mux2_2",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux2_4": _logic_module(
        "sky130_fd_sc_hd__mux2_4",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux2_8": _logic_module(
        "sky130_fd_sc_hd__mux2_8",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux2i_1": _logic_module(
        "sky130_fd_sc_hd__mux2i_1",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__mux2i_2": _logic_module(
        "sky130_fd_sc_hd__mux2i_2",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__mux2i_4": _logic_module(
        "sky130_fd_sc_hd__mux2i_4",
        "High Density",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__mux4_1": _logic_module(
        "sky130_fd_sc_hd__mux4_1",
        "High Density",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux4_2": _logic_module(
        "sky130_fd_sc_hd__mux4_2",
        "High Density",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__mux4_4": _logic_module(
        "sky130_fd_sc_hd__mux4_4",
        "High Density",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__nand2_1": _logic_module(
        "sky130_fd_sc_hd__nand2_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand2_2": _logic_module(
        "sky130_fd_sc_hd__nand2_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand2_4": _logic_module(
        "sky130_fd_sc_hd__nand2_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand2_8": _logic_module(
        "sky130_fd_sc_hd__nand2_8",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand2b_1": _logic_module(
        "sky130_fd_sc_hd__nand2b_1",
        "High Density",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand2b_2": _logic_module(
        "sky130_fd_sc_hd__nand2b_2",
        "High Density",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand2b_4": _logic_module(
        "sky130_fd_sc_hd__nand2b_4",
        "High Density",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand3_1": _logic_module(
        "sky130_fd_sc_hd__nand3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand3_2": _logic_module(
        "sky130_fd_sc_hd__nand3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand3_4": _logic_module(
        "sky130_fd_sc_hd__nand3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand3b_1": _logic_module(
        "sky130_fd_sc_hd__nand3b_1",
        "High Density",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand3b_2": _logic_module(
        "sky130_fd_sc_hd__nand3b_2",
        "High Density",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand3b_4": _logic_module(
        "sky130_fd_sc_hd__nand3b_4",
        "High Density",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4_1": _logic_module(
        "sky130_fd_sc_hd__nand4_1",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4_2": _logic_module(
        "sky130_fd_sc_hd__nand4_2",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4_4": _logic_module(
        "sky130_fd_sc_hd__nand4_4",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4b_1": _logic_module(
        "sky130_fd_sc_hd__nand4b_1",
        "High Density",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4b_2": _logic_module(
        "sky130_fd_sc_hd__nand4b_2",
        "High Density",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4b_4": _logic_module(
        "sky130_fd_sc_hd__nand4b_4",
        "High Density",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4bb_1": _logic_module(
        "sky130_fd_sc_hd__nand4bb_1",
        "High Density",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4bb_2": _logic_module(
        "sky130_fd_sc_hd__nand4bb_2",
        "High Density",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nand4bb_4": _logic_module(
        "sky130_fd_sc_hd__nand4bb_4",
        "High Density",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2_1": _logic_module(
        "sky130_fd_sc_hd__nor2_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2_2": _logic_module(
        "sky130_fd_sc_hd__nor2_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2_4": _logic_module(
        "sky130_fd_sc_hd__nor2_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2_8": _logic_module(
        "sky130_fd_sc_hd__nor2_8",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2b_1": _logic_module(
        "sky130_fd_sc_hd__nor2b_1",
        "High Density",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2b_2": _logic_module(
        "sky130_fd_sc_hd__nor2b_2",
        "High Density",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor2b_4": _logic_module(
        "sky130_fd_sc_hd__nor2b_4",
        "High Density",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor3_1": _logic_module(
        "sky130_fd_sc_hd__nor3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor3_2": _logic_module(
        "sky130_fd_sc_hd__nor3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor3_4": _logic_module(
        "sky130_fd_sc_hd__nor3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor3b_1": _logic_module(
        "sky130_fd_sc_hd__nor3b_1",
        "High Density",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor3b_2": _logic_module(
        "sky130_fd_sc_hd__nor3b_2",
        "High Density",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor3b_4": _logic_module(
        "sky130_fd_sc_hd__nor3b_4",
        "High Density",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4_1": _logic_module(
        "sky130_fd_sc_hd__nor4_1",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4_2": _logic_module(
        "sky130_fd_sc_hd__nor4_2",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4_4": _logic_module(
        "sky130_fd_sc_hd__nor4_4",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4b_1": _logic_module(
        "sky130_fd_sc_hd__nor4b_1",
        "High Density",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4b_2": _logic_module(
        "sky130_fd_sc_hd__nor4b_2",
        "High Density",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4b_4": _logic_module(
        "sky130_fd_sc_hd__nor4b_4",
        "High Density",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4bb_1": _logic_module(
        "sky130_fd_sc_hd__nor4bb_1",
        "High Density",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4bb_2": _logic_module(
        "sky130_fd_sc_hd__nor4bb_2",
        "High Density",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__nor4bb_4": _logic_module(
        "sky130_fd_sc_hd__nor4bb_4",
        "High Density",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o2bb2a_1": _logic_module(
        "sky130_fd_sc_hd__o2bb2a_1",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o2bb2a_2": _logic_module(
        "sky130_fd_sc_hd__o2bb2a_2",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o2bb2a_4": _logic_module(
        "sky130_fd_sc_hd__o2bb2a_4",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o2bb2ai_1": _logic_module(
        "sky130_fd_sc_hd__o2bb2ai_1",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o2bb2ai_2": _logic_module(
        "sky130_fd_sc_hd__o2bb2ai_2",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o2bb2ai_4": _logic_module(
        "sky130_fd_sc_hd__o2bb2ai_4",
        "High Density",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21a_1": _logic_module(
        "sky130_fd_sc_hd__o21a_1",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o21a_2": _logic_module(
        "sky130_fd_sc_hd__o21a_2",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o21a_4": _logic_module(
        "sky130_fd_sc_hd__o21a_4",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o21ai_0": _logic_module(
        "sky130_fd_sc_hd__o21ai_0",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21ai_1": _logic_module(
        "sky130_fd_sc_hd__o21ai_1",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21ai_2": _logic_module(
        "sky130_fd_sc_hd__o21ai_2",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21ai_4": _logic_module(
        "sky130_fd_sc_hd__o21ai_4",
        "High Density",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21ba_1": _logic_module(
        "sky130_fd_sc_hd__o21ba_1",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o21ba_2": _logic_module(
        "sky130_fd_sc_hd__o21ba_2",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o21ba_4": _logic_module(
        "sky130_fd_sc_hd__o21ba_4",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o21bai_1": _logic_module(
        "sky130_fd_sc_hd__o21bai_1",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21bai_2": _logic_module(
        "sky130_fd_sc_hd__o21bai_2",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o21bai_4": _logic_module(
        "sky130_fd_sc_hd__o21bai_4",
        "High Density",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o22a_1": _logic_module(
        "sky130_fd_sc_hd__o22a_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o22a_2": _logic_module(
        "sky130_fd_sc_hd__o22a_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o22a_4": _logic_module(
        "sky130_fd_sc_hd__o22a_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o22ai_1": _logic_module(
        "sky130_fd_sc_hd__o22ai_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o22ai_2": _logic_module(
        "sky130_fd_sc_hd__o22ai_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o22ai_4": _logic_module(
        "sky130_fd_sc_hd__o22ai_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o31a_1": _logic_module(
        "sky130_fd_sc_hd__o31a_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o31a_2": _logic_module(
        "sky130_fd_sc_hd__o31a_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o31a_4": _logic_module(
        "sky130_fd_sc_hd__o31a_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o31ai_1": _logic_module(
        "sky130_fd_sc_hd__o31ai_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o31ai_2": _logic_module(
        "sky130_fd_sc_hd__o31ai_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o31ai_4": _logic_module(
        "sky130_fd_sc_hd__o31ai_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o32a_1": _logic_module(
        "sky130_fd_sc_hd__o32a_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o32a_2": _logic_module(
        "sky130_fd_sc_hd__o32a_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o32a_4": _logic_module(
        "sky130_fd_sc_hd__o32a_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o32ai_1": _logic_module(
        "sky130_fd_sc_hd__o32ai_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o32ai_2": _logic_module(
        "sky130_fd_sc_hd__o32ai_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o32ai_4": _logic_module(
        "sky130_fd_sc_hd__o32ai_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o41a_1": _logic_module(
        "sky130_fd_sc_hd__o41a_1",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o41a_2": _logic_module(
        "sky130_fd_sc_hd__o41a_2",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o41a_4": _logic_module(
        "sky130_fd_sc_hd__o41a_4",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o41ai_1": _logic_module(
        "sky130_fd_sc_hd__o41ai_1",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o41ai_2": _logic_module(
        "sky130_fd_sc_hd__o41ai_2",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o41ai_4": _logic_module(
        "sky130_fd_sc_hd__o41ai_4",
        "High Density",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o211a_1": _logic_module(
        "sky130_fd_sc_hd__o211a_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o211a_2": _logic_module(
        "sky130_fd_sc_hd__o211a_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o211a_4": _logic_module(
        "sky130_fd_sc_hd__o211a_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o211ai_1": _logic_module(
        "sky130_fd_sc_hd__o211ai_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o211ai_2": _logic_module(
        "sky130_fd_sc_hd__o211ai_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o211ai_4": _logic_module(
        "sky130_fd_sc_hd__o211ai_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o221a_1": _logic_module(
        "sky130_fd_sc_hd__o221a_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o221a_2": _logic_module(
        "sky130_fd_sc_hd__o221a_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o221a_4": _logic_module(
        "sky130_fd_sc_hd__o221a_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o221ai_1": _logic_module(
        "sky130_fd_sc_hd__o221ai_1",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o221ai_2": _logic_module(
        "sky130_fd_sc_hd__o221ai_2",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o221ai_4": _logic_module(
        "sky130_fd_sc_hd__o221ai_4",
        "High Density",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o311a_1": _logic_module(
        "sky130_fd_sc_hd__o311a_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o311a_2": _logic_module(
        "sky130_fd_sc_hd__o311a_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o311a_4": _logic_module(
        "sky130_fd_sc_hd__o311a_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o311ai_0": _logic_module(
        "sky130_fd_sc_hd__o311ai_0",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o311ai_1": _logic_module(
        "sky130_fd_sc_hd__o311ai_1",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o311ai_2": _logic_module(
        "sky130_fd_sc_hd__o311ai_2",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o311ai_4": _logic_module(
        "sky130_fd_sc_hd__o311ai_4",
        "High Density",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o2111a_1": _logic_module(
        "sky130_fd_sc_hd__o2111a_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o2111a_2": _logic_module(
        "sky130_fd_sc_hd__o2111a_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o2111a_4": _logic_module(
        "sky130_fd_sc_hd__o2111a_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__o2111ai_1": _logic_module(
        "sky130_fd_sc_hd__o2111ai_1",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o2111ai_2": _logic_module(
        "sky130_fd_sc_hd__o2111ai_2",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__o2111ai_4": _logic_module(
        "sky130_fd_sc_hd__o2111ai_4",
        "High Density",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__or2_0": _logic_module(
        "sky130_fd_sc_hd__or2_0",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or2_1": _logic_module(
        "sky130_fd_sc_hd__or2_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or2_2": _logic_module(
        "sky130_fd_sc_hd__or2_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or2_4": _logic_module(
        "sky130_fd_sc_hd__or2_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or2b_1": _logic_module(
        "sky130_fd_sc_hd__or2b_1",
        "High Density",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or2b_2": _logic_module(
        "sky130_fd_sc_hd__or2b_2",
        "High Density",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or2b_4": _logic_module(
        "sky130_fd_sc_hd__or2b_4",
        "High Density",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or3_1": _logic_module(
        "sky130_fd_sc_hd__or3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or3_2": _logic_module(
        "sky130_fd_sc_hd__or3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or3_4": _logic_module(
        "sky130_fd_sc_hd__or3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or3b_1": _logic_module(
        "sky130_fd_sc_hd__or3b_1",
        "High Density",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or3b_2": _logic_module(
        "sky130_fd_sc_hd__or3b_2",
        "High Density",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or3b_4": _logic_module(
        "sky130_fd_sc_hd__or3b_4",
        "High Density",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4_1": _logic_module(
        "sky130_fd_sc_hd__or4_1",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4_2": _logic_module(
        "sky130_fd_sc_hd__or4_2",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4_4": _logic_module(
        "sky130_fd_sc_hd__or4_4",
        "High Density",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4b_1": _logic_module(
        "sky130_fd_sc_hd__or4b_1",
        "High Density",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4b_2": _logic_module(
        "sky130_fd_sc_hd__or4b_2",
        "High Density",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4b_4": _logic_module(
        "sky130_fd_sc_hd__or4b_4",
        "High Density",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4bb_1": _logic_module(
        "sky130_fd_sc_hd__or4bb_1",
        "High Density",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4bb_2": _logic_module(
        "sky130_fd_sc_hd__or4bb_2",
        "High Density",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__or4bb_4": _logic_module(
        "sky130_fd_sc_hd__or4bb_4",
        "High Density",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__probe_p_8": _logic_module(
        "sky130_fd_sc_hd__probe_p_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__probec_p_8": _logic_module(
        "sky130_fd_sc_hd__probec_p_8",
        "High Density",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__sdfbbn_1": _logic_module(
        "sky130_fd_sc_hd__sdfbbn_1",
        "High Density",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__sdfbbn_2": _logic_module(
        "sky130_fd_sc_hd__sdfbbn_2",
        "High Density",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hd__sdfbbp_1": _logic_module(
        "sky130_fd_sc_hd__sdfbbp_1",
        "High Density",
        [
            "CLK",
            "D",
            "RESET_B",
            "SCD",
            "SCE",
            "SET_B",
            "VGND",
            "VNB",
            "VPB",
            "VPWR",
            "Q",
        ],
    ),
    "sky130_fd_sc_hd__sdfrbp_1": _logic_module(
        "sky130_fd_sc_hd__sdfrbp_1",
        "High Density",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sdfrbp_2": _logic_module(
        "sky130_fd_sc_hd__sdfrbp_2",
        "High Density",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sdfrtn_1": _logic_module(
        "sky130_fd_sc_hd__sdfrtn_1",
        "High Density",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfrtp_1": _logic_module(
        "sky130_fd_sc_hd__sdfrtp_1",
        "High Density",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfrtp_2": _logic_module(
        "sky130_fd_sc_hd__sdfrtp_2",
        "High Density",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfrtp_4": _logic_module(
        "sky130_fd_sc_hd__sdfrtp_4",
        "High Density",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfsbp_1": _logic_module(
        "sky130_fd_sc_hd__sdfsbp_1",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sdfsbp_2": _logic_module(
        "sky130_fd_sc_hd__sdfsbp_2",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sdfstp_1": _logic_module(
        "sky130_fd_sc_hd__sdfstp_1",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfstp_2": _logic_module(
        "sky130_fd_sc_hd__sdfstp_2",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfstp_4": _logic_module(
        "sky130_fd_sc_hd__sdfstp_4",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfxbp_1": _logic_module(
        "sky130_fd_sc_hd__sdfxbp_1",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sdfxbp_2": _logic_module(
        "sky130_fd_sc_hd__sdfxbp_2",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sdfxtp_1": _logic_module(
        "sky130_fd_sc_hd__sdfxtp_1",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfxtp_2": _logic_module(
        "sky130_fd_sc_hd__sdfxtp_2",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdfxtp_4": _logic_module(
        "sky130_fd_sc_hd__sdfxtp_4",
        "High Density",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sdlclkp_1": _logic_module(
        "sky130_fd_sc_hd__sdlclkp_1",
        "High Density",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hd__sdlclkp_2": _logic_module(
        "sky130_fd_sc_hd__sdlclkp_2",
        "High Density",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hd__sdlclkp_4": _logic_module(
        "sky130_fd_sc_hd__sdlclkp_4",
        "High Density",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hd__sedfxbp_1": _logic_module(
        "sky130_fd_sc_hd__sedfxbp_1",
        "High Density",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sedfxbp_2": _logic_module(
        "sky130_fd_sc_hd__sedfxbp_2",
        "High Density",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hd__sedfxtp_1": _logic_module(
        "sky130_fd_sc_hd__sedfxtp_1",
        "High Density",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sedfxtp_2": _logic_module(
        "sky130_fd_sc_hd__sedfxtp_2",
        "High Density",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__sedfxtp_4": _logic_module(
        "sky130_fd_sc_hd__sedfxtp_4",
        "High Density",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hd__tap_1": _logic_module(
        "sky130_fd_sc_hd__tap_1", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__tap_2": _logic_module(
        "sky130_fd_sc_hd__tap_2", "High Density", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__tapvgnd2_1": _logic_module(
        "sky130_fd_sc_hd__tapvgnd2_1", "High Density", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__tapvgnd_1": _logic_module(
        "sky130_fd_sc_hd__tapvgnd_1", "High Density", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hd__tapvpwrvgnd_1": _logic_module(
        "sky130_fd_sc_hd__tapvpwrvgnd_1", "High Density", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_hd__xnor2_1": _logic_module(
        "sky130_fd_sc_hd__xnor2_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__xnor2_2": _logic_module(
        "sky130_fd_sc_hd__xnor2_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__xnor2_4": _logic_module(
        "sky130_fd_sc_hd__xnor2_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hd__xnor3_1": _logic_module(
        "sky130_fd_sc_hd__xnor3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xnor3_2": _logic_module(
        "sky130_fd_sc_hd__xnor3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xnor3_4": _logic_module(
        "sky130_fd_sc_hd__xnor3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xor2_1": _logic_module(
        "sky130_fd_sc_hd__xor2_1",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xor2_2": _logic_module(
        "sky130_fd_sc_hd__xor2_2",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xor2_4": _logic_module(
        "sky130_fd_sc_hd__xor2_4",
        "High Density",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xor3_1": _logic_module(
        "sky130_fd_sc_hd__xor3_1",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xor3_2": _logic_module(
        "sky130_fd_sc_hd__xor3_2",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hd__xor3_4": _logic_module(
        "sky130_fd_sc_hd__xor3_4",
        "High Density",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

hdll: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_hdll__a2bb2o_1": _logic_module(
        "sky130_fd_sc_hdll__a2bb2o_1",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a2bb2o_2": _logic_module(
        "sky130_fd_sc_hdll__a2bb2o_2",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a2bb2o_4": _logic_module(
        "sky130_fd_sc_hdll__a2bb2o_4",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a2bb2oi_1": _logic_module(
        "sky130_fd_sc_hdll__a2bb2oi_1",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a2bb2oi_2": _logic_module(
        "sky130_fd_sc_hdll__a2bb2oi_2",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a2bb2oi_4": _logic_module(
        "sky130_fd_sc_hdll__a2bb2oi_4",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a21bo_1": _logic_module(
        "sky130_fd_sc_hdll__a21bo_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21bo_2": _logic_module(
        "sky130_fd_sc_hdll__a21bo_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21bo_4": _logic_module(
        "sky130_fd_sc_hdll__a21bo_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21boi_1": _logic_module(
        "sky130_fd_sc_hdll__a21boi_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a21boi_2": _logic_module(
        "sky130_fd_sc_hdll__a21boi_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a21boi_4": _logic_module(
        "sky130_fd_sc_hdll__a21boi_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a21o_1": _logic_module(
        "sky130_fd_sc_hdll__a21o_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21o_2": _logic_module(
        "sky130_fd_sc_hdll__a21o_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21o_4": _logic_module(
        "sky130_fd_sc_hdll__a21o_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21o_6": _logic_module(
        "sky130_fd_sc_hdll__a21o_6",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21o_8": _logic_module(
        "sky130_fd_sc_hdll__a21o_8",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a21oi_1": _logic_module(
        "sky130_fd_sc_hdll__a21oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a21oi_2": _logic_module(
        "sky130_fd_sc_hdll__a21oi_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a21oi_4": _logic_module(
        "sky130_fd_sc_hdll__a21oi_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a22o_1": _logic_module(
        "sky130_fd_sc_hdll__a22o_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a22o_2": _logic_module(
        "sky130_fd_sc_hdll__a22o_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a22o_4": _logic_module(
        "sky130_fd_sc_hdll__a22o_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a22oi_1": _logic_module(
        "sky130_fd_sc_hdll__a22oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a22oi_2": _logic_module(
        "sky130_fd_sc_hdll__a22oi_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a22oi_4": _logic_module(
        "sky130_fd_sc_hdll__a22oi_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a31o_1": _logic_module(
        "sky130_fd_sc_hdll__a31o_1",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a31o_2": _logic_module(
        "sky130_fd_sc_hdll__a31o_2",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a31o_4": _logic_module(
        "sky130_fd_sc_hdll__a31o_4",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a31oi_1": _logic_module(
        "sky130_fd_sc_hdll__a31oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a31oi_2": _logic_module(
        "sky130_fd_sc_hdll__a31oi_2",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a31oi_4": _logic_module(
        "sky130_fd_sc_hdll__a31oi_4",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a32o_1": _logic_module(
        "sky130_fd_sc_hdll__a32o_1",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a32o_2": _logic_module(
        "sky130_fd_sc_hdll__a32o_2",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a32o_4": _logic_module(
        "sky130_fd_sc_hdll__a32o_4",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a32oi_1": _logic_module(
        "sky130_fd_sc_hdll__a32oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a32oi_2": _logic_module(
        "sky130_fd_sc_hdll__a32oi_2",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a32oi_4": _logic_module(
        "sky130_fd_sc_hdll__a32oi_4",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a211o_1": _logic_module(
        "sky130_fd_sc_hdll__a211o_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a211o_2": _logic_module(
        "sky130_fd_sc_hdll__a211o_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a211o_4": _logic_module(
        "sky130_fd_sc_hdll__a211o_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__a211oi_1": _logic_module(
        "sky130_fd_sc_hdll__a211oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a211oi_2": _logic_module(
        "sky130_fd_sc_hdll__a211oi_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a211oi_4": _logic_module(
        "sky130_fd_sc_hdll__a211oi_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a221oi_1": _logic_module(
        "sky130_fd_sc_hdll__a221oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a221oi_2": _logic_module(
        "sky130_fd_sc_hdll__a221oi_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a221oi_4": _logic_module(
        "sky130_fd_sc_hdll__a221oi_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__a222oi_1": _logic_module(
        "sky130_fd_sc_hdll__a222oi_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__and2_1": _logic_module(
        "sky130_fd_sc_hdll__and2_1",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2_2": _logic_module(
        "sky130_fd_sc_hdll__and2_2",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2_4": _logic_module(
        "sky130_fd_sc_hdll__and2_4",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2_6": _logic_module(
        "sky130_fd_sc_hdll__and2_6",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2_8": _logic_module(
        "sky130_fd_sc_hdll__and2_8",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2b_1": _logic_module(
        "sky130_fd_sc_hdll__and2b_1",
        "High Density Low Leakage",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2b_2": _logic_module(
        "sky130_fd_sc_hdll__and2b_2",
        "High Density Low Leakage",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and2b_4": _logic_module(
        "sky130_fd_sc_hdll__and2b_4",
        "High Density Low Leakage",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and3_1": _logic_module(
        "sky130_fd_sc_hdll__and3_1",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and3_2": _logic_module(
        "sky130_fd_sc_hdll__and3_2",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and3_4": _logic_module(
        "sky130_fd_sc_hdll__and3_4",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and3b_1": _logic_module(
        "sky130_fd_sc_hdll__and3b_1",
        "High Density Low Leakage",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and3b_2": _logic_module(
        "sky130_fd_sc_hdll__and3b_2",
        "High Density Low Leakage",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and3b_4": _logic_module(
        "sky130_fd_sc_hdll__and3b_4",
        "High Density Low Leakage",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4_1": _logic_module(
        "sky130_fd_sc_hdll__and4_1",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4_2": _logic_module(
        "sky130_fd_sc_hdll__and4_2",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4_4": _logic_module(
        "sky130_fd_sc_hdll__and4_4",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4b_1": _logic_module(
        "sky130_fd_sc_hdll__and4b_1",
        "High Density Low Leakage",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4b_2": _logic_module(
        "sky130_fd_sc_hdll__and4b_2",
        "High Density Low Leakage",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4b_4": _logic_module(
        "sky130_fd_sc_hdll__and4b_4",
        "High Density Low Leakage",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4bb_1": _logic_module(
        "sky130_fd_sc_hdll__and4bb_1",
        "High Density Low Leakage",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4bb_2": _logic_module(
        "sky130_fd_sc_hdll__and4bb_2",
        "High Density Low Leakage",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__and4bb_4": _logic_module(
        "sky130_fd_sc_hdll__and4bb_4",
        "High Density Low Leakage",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_1": _logic_module(
        "sky130_fd_sc_hdll__buf_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_2": _logic_module(
        "sky130_fd_sc_hdll__buf_2",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_4": _logic_module(
        "sky130_fd_sc_hdll__buf_4",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_6": _logic_module(
        "sky130_fd_sc_hdll__buf_6",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_8": _logic_module(
        "sky130_fd_sc_hdll__buf_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_12": _logic_module(
        "sky130_fd_sc_hdll__buf_12",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__buf_16": _logic_module(
        "sky130_fd_sc_hdll__buf_16",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__bufbuf_8": _logic_module(
        "sky130_fd_sc_hdll__bufbuf_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__bufbuf_16": _logic_module(
        "sky130_fd_sc_hdll__bufbuf_16",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__bufinv_8": _logic_module(
        "sky130_fd_sc_hdll__bufinv_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__bufinv_16": _logic_module(
        "sky130_fd_sc_hdll__bufinv_16",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkbuf_1": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkbuf_2": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_2",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkbuf_4": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_4",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkbuf_6": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_6",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkbuf_8": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkbuf_12": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_12",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkbuf_16": _logic_module(
        "sky130_fd_sc_hdll__clkbuf_16",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkinv_1": _logic_module(
        "sky130_fd_sc_hdll__clkinv_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinv_2": _logic_module(
        "sky130_fd_sc_hdll__clkinv_2",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinv_4": _logic_module(
        "sky130_fd_sc_hdll__clkinv_4",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinv_8": _logic_module(
        "sky130_fd_sc_hdll__clkinv_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinv_12": _logic_module(
        "sky130_fd_sc_hdll__clkinv_12",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinv_16": _logic_module(
        "sky130_fd_sc_hdll__clkinv_16",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinvlp_2": _logic_module(
        "sky130_fd_sc_hdll__clkinvlp_2",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkinvlp_4": _logic_module(
        "sky130_fd_sc_hdll__clkinvlp_4",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__clkmux2_1": _logic_module(
        "sky130_fd_sc_hdll__clkmux2_1",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkmux2_2": _logic_module(
        "sky130_fd_sc_hdll__clkmux2_2",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__clkmux2_4": _logic_module(
        "sky130_fd_sc_hdll__clkmux2_4",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__conb_1": _logic_module(
        "sky130_fd_sc_hdll__conb_1",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_hdll__decap_3": _logic_module(
        "sky130_fd_sc_hdll__decap_3",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__decap_4": _logic_module(
        "sky130_fd_sc_hdll__decap_4",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__decap_6": _logic_module(
        "sky130_fd_sc_hdll__decap_6",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__decap_8": _logic_module(
        "sky130_fd_sc_hdll__decap_8",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__decap_12": _logic_module(
        "sky130_fd_sc_hdll__decap_12",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__dfrtp_1": _logic_module(
        "sky130_fd_sc_hdll__dfrtp_1",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dfrtp_2": _logic_module(
        "sky130_fd_sc_hdll__dfrtp_2",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dfrtp_4": _logic_module(
        "sky130_fd_sc_hdll__dfrtp_4",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dfstp_1": _logic_module(
        "sky130_fd_sc_hdll__dfstp_1",
        "High Density Low Leakage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dfstp_2": _logic_module(
        "sky130_fd_sc_hdll__dfstp_2",
        "High Density Low Leakage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dfstp_4": _logic_module(
        "sky130_fd_sc_hdll__dfstp_4",
        "High Density Low Leakage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__diode_2": _logic_module(
        "sky130_fd_sc_hdll__diode_2",
        "High Density Low Leakage",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__diode_4": _logic_module(
        "sky130_fd_sc_hdll__diode_4",
        "High Density Low Leakage",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__diode_6": _logic_module(
        "sky130_fd_sc_hdll__diode_6",
        "High Density Low Leakage",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__diode_8": _logic_module(
        "sky130_fd_sc_hdll__diode_8",
        "High Density Low Leakage",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__dlrtn_1": _logic_module(
        "sky130_fd_sc_hdll__dlrtn_1",
        "High Density Low Leakage",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlrtn_2": _logic_module(
        "sky130_fd_sc_hdll__dlrtn_2",
        "High Density Low Leakage",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlrtn_4": _logic_module(
        "sky130_fd_sc_hdll__dlrtn_4",
        "High Density Low Leakage",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlrtp_1": _logic_module(
        "sky130_fd_sc_hdll__dlrtp_1",
        "High Density Low Leakage",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlrtp_2": _logic_module(
        "sky130_fd_sc_hdll__dlrtp_2",
        "High Density Low Leakage",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlrtp_4": _logic_module(
        "sky130_fd_sc_hdll__dlrtp_4",
        "High Density Low Leakage",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlxtn_1": _logic_module(
        "sky130_fd_sc_hdll__dlxtn_1",
        "High Density Low Leakage",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlxtn_2": _logic_module(
        "sky130_fd_sc_hdll__dlxtn_2",
        "High Density Low Leakage",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlxtn_4": _logic_module(
        "sky130_fd_sc_hdll__dlxtn_4",
        "High Density Low Leakage",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__dlygate4sd1_1": _logic_module(
        "sky130_fd_sc_hdll__dlygate4sd1_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__dlygate4sd2_1": _logic_module(
        "sky130_fd_sc_hdll__dlygate4sd2_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__dlygate4sd3_1": _logic_module(
        "sky130_fd_sc_hdll__dlygate4sd3_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__ebufn_1": _logic_module(
        "sky130_fd_sc_hdll__ebufn_1",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__ebufn_2": _logic_module(
        "sky130_fd_sc_hdll__ebufn_2",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__ebufn_4": _logic_module(
        "sky130_fd_sc_hdll__ebufn_4",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__ebufn_8": _logic_module(
        "sky130_fd_sc_hdll__ebufn_8",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvn_1": _logic_module(
        "sky130_fd_sc_hdll__einvn_1",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvn_2": _logic_module(
        "sky130_fd_sc_hdll__einvn_2",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvn_4": _logic_module(
        "sky130_fd_sc_hdll__einvn_4",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvn_8": _logic_module(
        "sky130_fd_sc_hdll__einvn_8",
        "High Density Low Leakage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvp_1": _logic_module(
        "sky130_fd_sc_hdll__einvp_1",
        "High Density Low Leakage",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvp_2": _logic_module(
        "sky130_fd_sc_hdll__einvp_2",
        "High Density Low Leakage",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvp_4": _logic_module(
        "sky130_fd_sc_hdll__einvp_4",
        "High Density Low Leakage",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__einvp_8": _logic_module(
        "sky130_fd_sc_hdll__einvp_8",
        "High Density Low Leakage",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hdll__fill_1": _logic_module(
        "sky130_fd_sc_hdll__fill_1",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__fill_2": _logic_module(
        "sky130_fd_sc_hdll__fill_2",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__fill_4": _logic_module(
        "sky130_fd_sc_hdll__fill_4",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__fill_8": _logic_module(
        "sky130_fd_sc_hdll__fill_8",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__inputiso0n_1": _logic_module(
        "sky130_fd_sc_hdll__inputiso0n_1",
        "High Density Low Leakage",
        ["A", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__inputiso0p_1": _logic_module(
        "sky130_fd_sc_hdll__inputiso0p_1",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__inputiso1n_1": _logic_module(
        "sky130_fd_sc_hdll__inputiso1n_1",
        "High Density Low Leakage",
        ["A", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__inputiso1p_1": _logic_module(
        "sky130_fd_sc_hdll__inputiso1p_1",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__inv_1": _logic_module(
        "sky130_fd_sc_hdll__inv_1",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__inv_2": _logic_module(
        "sky130_fd_sc_hdll__inv_2",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__inv_4": _logic_module(
        "sky130_fd_sc_hdll__inv_4",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__inv_6": _logic_module(
        "sky130_fd_sc_hdll__inv_6",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__inv_8": _logic_module(
        "sky130_fd_sc_hdll__inv_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__inv_12": _logic_module(
        "sky130_fd_sc_hdll__inv_12",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__inv_16": _logic_module(
        "sky130_fd_sc_hdll__inv_16",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__isobufsrc_1": _logic_module(
        "sky130_fd_sc_hdll__isobufsrc_1",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__isobufsrc_2": _logic_module(
        "sky130_fd_sc_hdll__isobufsrc_2",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__isobufsrc_4": _logic_module(
        "sky130_fd_sc_hdll__isobufsrc_4",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__isobufsrc_8": _logic_module(
        "sky130_fd_sc_hdll__isobufsrc_8",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__isobufsrc_16": _logic_module(
        "sky130_fd_sc_hdll__isobufsrc_16",
        "High Density Low Leakage",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2_1": _logic_module(
        "sky130_fd_sc_hdll__mux2_1",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2_2": _logic_module(
        "sky130_fd_sc_hdll__mux2_2",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2_4": _logic_module(
        "sky130_fd_sc_hdll__mux2_4",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2_8": _logic_module(
        "sky130_fd_sc_hdll__mux2_8",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2_12": _logic_module(
        "sky130_fd_sc_hdll__mux2_12",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2_16": _logic_module(
        "sky130_fd_sc_hdll__mux2_16",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__mux2i_1": _logic_module(
        "sky130_fd_sc_hdll__mux2i_1",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__mux2i_2": _logic_module(
        "sky130_fd_sc_hdll__mux2i_2",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__mux2i_4": _logic_module(
        "sky130_fd_sc_hdll__mux2i_4",
        "High Density Low Leakage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__muxb4to1_1": _logic_module(
        "sky130_fd_sc_hdll__muxb4to1_1",
        "High Density Low Leakage",
        ["D[3]", "D[2]", "D[1]", "D[0]", "S[3]", "S[2]", "S[1]", "S[0]", "VGND"],
    ),
    "sky130_fd_sc_hdll__muxb4to1_2": _logic_module(
        "sky130_fd_sc_hdll__muxb4to1_2",
        "High Density Low Leakage",
        ["D[3]", "D[2]", "D[1]", "D[0]", "S[3]", "S[2]", "S[1]", "S[0]", "VGND"],
    ),
    "sky130_fd_sc_hdll__muxb4to1_4": _logic_module(
        "sky130_fd_sc_hdll__muxb4to1_4",
        "High Density Low Leakage",
        ["D[3]", "D[2]", "D[1]", "D[0]", "S[3]", "S[2]", "S[1]", "S[0]", "VGND"],
    ),
    "sky130_fd_sc_hdll__muxb8to1_1": _logic_module(
        "sky130_fd_sc_hdll__muxb8to1_1",
        "High Density Low Leakage",
        ["D[7]", "D[6]", "D[5]", "D[4]", "D[3]", "D[2]", "D[1]", "D[0]", "S[7]"],
    ),
    "sky130_fd_sc_hdll__muxb8to1_2": _logic_module(
        "sky130_fd_sc_hdll__muxb8to1_2",
        "High Density Low Leakage",
        ["D[7]", "D[6]", "D[5]", "D[4]", "D[3]", "D[2]", "D[1]", "D[0]", "S[7]"],
    ),
    "sky130_fd_sc_hdll__muxb8to1_4": _logic_module(
        "sky130_fd_sc_hdll__muxb8to1_4",
        "High Density Low Leakage",
        ["D[7]", "D[6]", "D[5]", "D[4]", "D[3]", "D[2]", "D[1]", "D[0]", "S[7]"],
    ),
    "sky130_fd_sc_hdll__muxb16to1_1": _logic_module(
        "sky130_fd_sc_hdll__muxb16to1_1",
        "High Density Low Leakage",
        ["D[15]", "D[14]", "D[13]", "D[12]", "D[11]", "D[10]", "D[9]", "D[8]"],
    ),
    "sky130_fd_sc_hdll__muxb16to1_2": _logic_module(
        "sky130_fd_sc_hdll__muxb16to1_2",
        "High Density Low Leakage",
        ["D[15]", "D[14]", "D[13]", "D[12]", "D[11]", "D[10]", "D[9]", "D[8]"],
    ),
    "sky130_fd_sc_hdll__muxb16to1_4": _logic_module(
        "sky130_fd_sc_hdll__muxb16to1_4",
        "High Density Low Leakage",
        ["D[15]", "D[14]", "D[13]", "D[12]", "D[11]", "D[10]", "D[9]", "D[8]"],
    ),
    "sky130_fd_sc_hdll__nand2_1": _logic_module(
        "sky130_fd_sc_hdll__nand2_1",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2_2": _logic_module(
        "sky130_fd_sc_hdll__nand2_2",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2_4": _logic_module(
        "sky130_fd_sc_hdll__nand2_4",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2_6": _logic_module(
        "sky130_fd_sc_hdll__nand2_6",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2_8": _logic_module(
        "sky130_fd_sc_hdll__nand2_8",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2_12": _logic_module(
        "sky130_fd_sc_hdll__nand2_12",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2_16": _logic_module(
        "sky130_fd_sc_hdll__nand2_16",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2b_1": _logic_module(
        "sky130_fd_sc_hdll__nand2b_1",
        "High Density Low Leakage",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2b_2": _logic_module(
        "sky130_fd_sc_hdll__nand2b_2",
        "High Density Low Leakage",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand2b_4": _logic_module(
        "sky130_fd_sc_hdll__nand2b_4",
        "High Density Low Leakage",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand3_1": _logic_module(
        "sky130_fd_sc_hdll__nand3_1",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand3_2": _logic_module(
        "sky130_fd_sc_hdll__nand3_2",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand3_4": _logic_module(
        "sky130_fd_sc_hdll__nand3_4",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand3b_1": _logic_module(
        "sky130_fd_sc_hdll__nand3b_1",
        "High Density Low Leakage",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand3b_2": _logic_module(
        "sky130_fd_sc_hdll__nand3b_2",
        "High Density Low Leakage",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand3b_4": _logic_module(
        "sky130_fd_sc_hdll__nand3b_4",
        "High Density Low Leakage",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4_1": _logic_module(
        "sky130_fd_sc_hdll__nand4_1",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4_2": _logic_module(
        "sky130_fd_sc_hdll__nand4_2",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4_4": _logic_module(
        "sky130_fd_sc_hdll__nand4_4",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4b_1": _logic_module(
        "sky130_fd_sc_hdll__nand4b_1",
        "High Density Low Leakage",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4b_2": _logic_module(
        "sky130_fd_sc_hdll__nand4b_2",
        "High Density Low Leakage",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4b_4": _logic_module(
        "sky130_fd_sc_hdll__nand4b_4",
        "High Density Low Leakage",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4bb_1": _logic_module(
        "sky130_fd_sc_hdll__nand4bb_1",
        "High Density Low Leakage",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4bb_2": _logic_module(
        "sky130_fd_sc_hdll__nand4bb_2",
        "High Density Low Leakage",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nand4bb_4": _logic_module(
        "sky130_fd_sc_hdll__nand4bb_4",
        "High Density Low Leakage",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2_1": _logic_module(
        "sky130_fd_sc_hdll__nor2_1",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2_2": _logic_module(
        "sky130_fd_sc_hdll__nor2_2",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2_4": _logic_module(
        "sky130_fd_sc_hdll__nor2_4",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2_8": _logic_module(
        "sky130_fd_sc_hdll__nor2_8",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2b_1": _logic_module(
        "sky130_fd_sc_hdll__nor2b_1",
        "High Density Low Leakage",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2b_2": _logic_module(
        "sky130_fd_sc_hdll__nor2b_2",
        "High Density Low Leakage",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor2b_4": _logic_module(
        "sky130_fd_sc_hdll__nor2b_4",
        "High Density Low Leakage",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor3_1": _logic_module(
        "sky130_fd_sc_hdll__nor3_1",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor3_2": _logic_module(
        "sky130_fd_sc_hdll__nor3_2",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor3_4": _logic_module(
        "sky130_fd_sc_hdll__nor3_4",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor3b_1": _logic_module(
        "sky130_fd_sc_hdll__nor3b_1",
        "High Density Low Leakage",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor3b_2": _logic_module(
        "sky130_fd_sc_hdll__nor3b_2",
        "High Density Low Leakage",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor3b_4": _logic_module(
        "sky130_fd_sc_hdll__nor3b_4",
        "High Density Low Leakage",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4_1": _logic_module(
        "sky130_fd_sc_hdll__nor4_1",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4_2": _logic_module(
        "sky130_fd_sc_hdll__nor4_2",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4_4": _logic_module(
        "sky130_fd_sc_hdll__nor4_4",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4_6": _logic_module(
        "sky130_fd_sc_hdll__nor4_6",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4_8": _logic_module(
        "sky130_fd_sc_hdll__nor4_8",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4b_1": _logic_module(
        "sky130_fd_sc_hdll__nor4b_1",
        "High Density Low Leakage",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4b_2": _logic_module(
        "sky130_fd_sc_hdll__nor4b_2",
        "High Density Low Leakage",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4b_4": _logic_module(
        "sky130_fd_sc_hdll__nor4b_4",
        "High Density Low Leakage",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4bb_1": _logic_module(
        "sky130_fd_sc_hdll__nor4bb_1",
        "High Density Low Leakage",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4bb_2": _logic_module(
        "sky130_fd_sc_hdll__nor4bb_2",
        "High Density Low Leakage",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__nor4bb_4": _logic_module(
        "sky130_fd_sc_hdll__nor4bb_4",
        "High Density Low Leakage",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o2bb2a_1": _logic_module(
        "sky130_fd_sc_hdll__o2bb2a_1",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o2bb2a_2": _logic_module(
        "sky130_fd_sc_hdll__o2bb2a_2",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o2bb2a_4": _logic_module(
        "sky130_fd_sc_hdll__o2bb2a_4",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o2bb2ai_1": _logic_module(
        "sky130_fd_sc_hdll__o2bb2ai_1",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o2bb2ai_2": _logic_module(
        "sky130_fd_sc_hdll__o2bb2ai_2",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o2bb2ai_4": _logic_module(
        "sky130_fd_sc_hdll__o2bb2ai_4",
        "High Density Low Leakage",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o21a_1": _logic_module(
        "sky130_fd_sc_hdll__o21a_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o21a_2": _logic_module(
        "sky130_fd_sc_hdll__o21a_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o21a_4": _logic_module(
        "sky130_fd_sc_hdll__o21a_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o21ai_1": _logic_module(
        "sky130_fd_sc_hdll__o21ai_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o21ai_2": _logic_module(
        "sky130_fd_sc_hdll__o21ai_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o21ai_4": _logic_module(
        "sky130_fd_sc_hdll__o21ai_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o21ba_1": _logic_module(
        "sky130_fd_sc_hdll__o21ba_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o21ba_2": _logic_module(
        "sky130_fd_sc_hdll__o21ba_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o21ba_4": _logic_module(
        "sky130_fd_sc_hdll__o21ba_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o21bai_1": _logic_module(
        "sky130_fd_sc_hdll__o21bai_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o21bai_2": _logic_module(
        "sky130_fd_sc_hdll__o21bai_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o21bai_4": _logic_module(
        "sky130_fd_sc_hdll__o21bai_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o22a_1": _logic_module(
        "sky130_fd_sc_hdll__o22a_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o22a_2": _logic_module(
        "sky130_fd_sc_hdll__o22a_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o22a_4": _logic_module(
        "sky130_fd_sc_hdll__o22a_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o22ai_1": _logic_module(
        "sky130_fd_sc_hdll__o22ai_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o22ai_2": _logic_module(
        "sky130_fd_sc_hdll__o22ai_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o22ai_4": _logic_module(
        "sky130_fd_sc_hdll__o22ai_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o31ai_1": _logic_module(
        "sky130_fd_sc_hdll__o31ai_1",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o31ai_2": _logic_module(
        "sky130_fd_sc_hdll__o31ai_2",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o31ai_4": _logic_module(
        "sky130_fd_sc_hdll__o31ai_4",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o32ai_1": _logic_module(
        "sky130_fd_sc_hdll__o32ai_1",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o32ai_2": _logic_module(
        "sky130_fd_sc_hdll__o32ai_2",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o32ai_4": _logic_module(
        "sky130_fd_sc_hdll__o32ai_4",
        "High Density Low Leakage",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o211a_1": _logic_module(
        "sky130_fd_sc_hdll__o211a_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o211a_2": _logic_module(
        "sky130_fd_sc_hdll__o211a_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o211a_4": _logic_module(
        "sky130_fd_sc_hdll__o211a_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o211ai_1": _logic_module(
        "sky130_fd_sc_hdll__o211ai_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o211ai_2": _logic_module(
        "sky130_fd_sc_hdll__o211ai_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o211ai_4": _logic_module(
        "sky130_fd_sc_hdll__o211ai_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o221a_1": _logic_module(
        "sky130_fd_sc_hdll__o221a_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o221a_2": _logic_module(
        "sky130_fd_sc_hdll__o221a_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o221a_4": _logic_module(
        "sky130_fd_sc_hdll__o221a_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__o221ai_1": _logic_module(
        "sky130_fd_sc_hdll__o221ai_1",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o221ai_2": _logic_module(
        "sky130_fd_sc_hdll__o221ai_2",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__o221ai_4": _logic_module(
        "sky130_fd_sc_hdll__o221ai_4",
        "High Density Low Leakage",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__or2_1": _logic_module(
        "sky130_fd_sc_hdll__or2_1",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2_2": _logic_module(
        "sky130_fd_sc_hdll__or2_2",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2_4": _logic_module(
        "sky130_fd_sc_hdll__or2_4",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2_6": _logic_module(
        "sky130_fd_sc_hdll__or2_6",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2_8": _logic_module(
        "sky130_fd_sc_hdll__or2_8",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2b_1": _logic_module(
        "sky130_fd_sc_hdll__or2b_1",
        "High Density Low Leakage",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2b_2": _logic_module(
        "sky130_fd_sc_hdll__or2b_2",
        "High Density Low Leakage",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or2b_4": _logic_module(
        "sky130_fd_sc_hdll__or2b_4",
        "High Density Low Leakage",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or3_1": _logic_module(
        "sky130_fd_sc_hdll__or3_1",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or3_2": _logic_module(
        "sky130_fd_sc_hdll__or3_2",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or3_4": _logic_module(
        "sky130_fd_sc_hdll__or3_4",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or3b_1": _logic_module(
        "sky130_fd_sc_hdll__or3b_1",
        "High Density Low Leakage",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or3b_2": _logic_module(
        "sky130_fd_sc_hdll__or3b_2",
        "High Density Low Leakage",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or3b_4": _logic_module(
        "sky130_fd_sc_hdll__or3b_4",
        "High Density Low Leakage",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4_1": _logic_module(
        "sky130_fd_sc_hdll__or4_1",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4_2": _logic_module(
        "sky130_fd_sc_hdll__or4_2",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4_4": _logic_module(
        "sky130_fd_sc_hdll__or4_4",
        "High Density Low Leakage",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4b_1": _logic_module(
        "sky130_fd_sc_hdll__or4b_1",
        "High Density Low Leakage",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4b_2": _logic_module(
        "sky130_fd_sc_hdll__or4b_2",
        "High Density Low Leakage",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4b_4": _logic_module(
        "sky130_fd_sc_hdll__or4b_4",
        "High Density Low Leakage",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4bb_1": _logic_module(
        "sky130_fd_sc_hdll__or4bb_1",
        "High Density Low Leakage",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4bb_2": _logic_module(
        "sky130_fd_sc_hdll__or4bb_2",
        "High Density Low Leakage",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__or4bb_4": _logic_module(
        "sky130_fd_sc_hdll__or4bb_4",
        "High Density Low Leakage",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__probe_p_8": _logic_module(
        "sky130_fd_sc_hdll__probe_p_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__probec_p_8": _logic_module(
        "sky130_fd_sc_hdll__probec_p_8",
        "High Density Low Leakage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__sdfbbp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfbbp_1",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__sdfrbp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfrbp_1",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sdfrbp_2": _logic_module(
        "sky130_fd_sc_hdll__sdfrbp_2",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sdfrtn_1": _logic_module(
        "sky130_fd_sc_hdll__sdfrtn_1",
        "High Density Low Leakage",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfrtp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfrtp_1",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfrtp_2": _logic_module(
        "sky130_fd_sc_hdll__sdfrtp_2",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfrtp_4": _logic_module(
        "sky130_fd_sc_hdll__sdfrtp_4",
        "High Density Low Leakage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfsbp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfsbp_1",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sdfsbp_2": _logic_module(
        "sky130_fd_sc_hdll__sdfsbp_2",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sdfstp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfstp_1",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfstp_2": _logic_module(
        "sky130_fd_sc_hdll__sdfstp_2",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfstp_4": _logic_module(
        "sky130_fd_sc_hdll__sdfstp_4",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfxbp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfxbp_1",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sdfxbp_2": _logic_module(
        "sky130_fd_sc_hdll__sdfxbp_2",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sdfxtp_1": _logic_module(
        "sky130_fd_sc_hdll__sdfxtp_1",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfxtp_2": _logic_module(
        "sky130_fd_sc_hdll__sdfxtp_2",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdfxtp_4": _logic_module(
        "sky130_fd_sc_hdll__sdfxtp_4",
        "High Density Low Leakage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hdll__sdlclkp_1": _logic_module(
        "sky130_fd_sc_hdll__sdlclkp_1",
        "High Density Low Leakage",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hdll__sdlclkp_2": _logic_module(
        "sky130_fd_sc_hdll__sdlclkp_2",
        "High Density Low Leakage",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hdll__sdlclkp_4": _logic_module(
        "sky130_fd_sc_hdll__sdlclkp_4",
        "High Density Low Leakage",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hdll__sedfxbp_1": _logic_module(
        "sky130_fd_sc_hdll__sedfxbp_1",
        "High Density Low Leakage",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__sedfxbp_2": _logic_module(
        "sky130_fd_sc_hdll__sedfxbp_2",
        "High Density Low Leakage",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hdll__tap": _logic_module(
        "sky130_fd_sc_hdll__tap", "High Density Low Leakage", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_hdll__tap_1": _logic_module(
        "sky130_fd_sc_hdll__tap_1",
        "High Density Low Leakage",
        ["VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__tapvgnd2_1": _logic_module(
        "sky130_fd_sc_hdll__tapvgnd2_1",
        "High Density Low Leakage",
        ["VGND", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__tapvgnd_1": _logic_module(
        "sky130_fd_sc_hdll__tapvgnd_1",
        "High Density Low Leakage",
        ["VGND", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hdll__tapvpwrvgnd_1": _logic_module(
        "sky130_fd_sc_hdll__tapvpwrvgnd_1", "High Density Low Leakage", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_hdll__xnor2_1": _logic_module(
        "sky130_fd_sc_hdll__xnor2_1",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__xnor2_2": _logic_module(
        "sky130_fd_sc_hdll__xnor2_2",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__xnor2_4": _logic_module(
        "sky130_fd_sc_hdll__xnor2_4",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hdll__xnor3_1": _logic_module(
        "sky130_fd_sc_hdll__xnor3_1",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xnor3_2": _logic_module(
        "sky130_fd_sc_hdll__xnor3_2",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xnor3_4": _logic_module(
        "sky130_fd_sc_hdll__xnor3_4",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xor2_1": _logic_module(
        "sky130_fd_sc_hdll__xor2_1",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xor2_2": _logic_module(
        "sky130_fd_sc_hdll__xor2_2",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xor2_4": _logic_module(
        "sky130_fd_sc_hdll__xor2_4",
        "High Density Low Leakage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xor3_1": _logic_module(
        "sky130_fd_sc_hdll__xor3_1",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xor3_2": _logic_module(
        "sky130_fd_sc_hdll__xor3_2",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hdll__xor3_4": _logic_module(
        "sky130_fd_sc_hdll__xor3_4",
        "High Density Low Leakage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

hs: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_hs__a2bb2o_1": _logic_module(
        "sky130_fd_sc_hs__a2bb2o_1",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a2bb2o_2": _logic_module(
        "sky130_fd_sc_hs__a2bb2o_2",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a2bb2o_4": _logic_module(
        "sky130_fd_sc_hs__a2bb2o_4",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a2bb2oi_1": _logic_module(
        "sky130_fd_sc_hs__a2bb2oi_1",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a2bb2oi_2": _logic_module(
        "sky130_fd_sc_hs__a2bb2oi_2",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a2bb2oi_4": _logic_module(
        "sky130_fd_sc_hs__a2bb2oi_4",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a21bo_1": _logic_module(
        "sky130_fd_sc_hs__a21bo_1",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a21bo_2": _logic_module(
        "sky130_fd_sc_hs__a21bo_2",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a21bo_4": _logic_module(
        "sky130_fd_sc_hs__a21bo_4",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a21boi_1": _logic_module(
        "sky130_fd_sc_hs__a21boi_1",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a21boi_2": _logic_module(
        "sky130_fd_sc_hs__a21boi_2",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a21boi_4": _logic_module(
        "sky130_fd_sc_hs__a21boi_4",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a21o_1": _logic_module(
        "sky130_fd_sc_hs__a21o_1",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a21o_2": _logic_module(
        "sky130_fd_sc_hs__a21o_2",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a21o_4": _logic_module(
        "sky130_fd_sc_hs__a21o_4",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a21oi_1": _logic_module(
        "sky130_fd_sc_hs__a21oi_1",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a21oi_2": _logic_module(
        "sky130_fd_sc_hs__a21oi_2",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a21oi_4": _logic_module(
        "sky130_fd_sc_hs__a21oi_4",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a22o_1": _logic_module(
        "sky130_fd_sc_hs__a22o_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a22o_2": _logic_module(
        "sky130_fd_sc_hs__a22o_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a22o_4": _logic_module(
        "sky130_fd_sc_hs__a22o_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a22oi_1": _logic_module(
        "sky130_fd_sc_hs__a22oi_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a22oi_2": _logic_module(
        "sky130_fd_sc_hs__a22oi_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a22oi_4": _logic_module(
        "sky130_fd_sc_hs__a22oi_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a31o_1": _logic_module(
        "sky130_fd_sc_hs__a31o_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a31o_2": _logic_module(
        "sky130_fd_sc_hs__a31o_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a31o_4": _logic_module(
        "sky130_fd_sc_hs__a31o_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a31oi_1": _logic_module(
        "sky130_fd_sc_hs__a31oi_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a31oi_2": _logic_module(
        "sky130_fd_sc_hs__a31oi_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a31oi_4": _logic_module(
        "sky130_fd_sc_hs__a31oi_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a32o_1": _logic_module(
        "sky130_fd_sc_hs__a32o_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a32o_2": _logic_module(
        "sky130_fd_sc_hs__a32o_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a32o_4": _logic_module(
        "sky130_fd_sc_hs__a32o_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a32oi_1": _logic_module(
        "sky130_fd_sc_hs__a32oi_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a32oi_2": _logic_module(
        "sky130_fd_sc_hs__a32oi_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a32oi_4": _logic_module(
        "sky130_fd_sc_hs__a32oi_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a41o_1": _logic_module(
        "sky130_fd_sc_hs__a41o_1",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a41o_2": _logic_module(
        "sky130_fd_sc_hs__a41o_2",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a41o_4": _logic_module(
        "sky130_fd_sc_hs__a41o_4",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a41oi_1": _logic_module(
        "sky130_fd_sc_hs__a41oi_1",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a41oi_2": _logic_module(
        "sky130_fd_sc_hs__a41oi_2",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a41oi_4": _logic_module(
        "sky130_fd_sc_hs__a41oi_4",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a211o_1": _logic_module(
        "sky130_fd_sc_hs__a211o_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a211o_2": _logic_module(
        "sky130_fd_sc_hs__a211o_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a211o_4": _logic_module(
        "sky130_fd_sc_hs__a211o_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a211oi_1": _logic_module(
        "sky130_fd_sc_hs__a211oi_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a211oi_2": _logic_module(
        "sky130_fd_sc_hs__a211oi_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a211oi_4": _logic_module(
        "sky130_fd_sc_hs__a211oi_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a221o_1": _logic_module(
        "sky130_fd_sc_hs__a221o_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a221o_2": _logic_module(
        "sky130_fd_sc_hs__a221o_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a221o_4": _logic_module(
        "sky130_fd_sc_hs__a221o_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a221oi_1": _logic_module(
        "sky130_fd_sc_hs__a221oi_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a221oi_2": _logic_module(
        "sky130_fd_sc_hs__a221oi_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a221oi_4": _logic_module(
        "sky130_fd_sc_hs__a221oi_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a222o_1": _logic_module(
        "sky130_fd_sc_hs__a222o_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a222o_2": _logic_module(
        "sky130_fd_sc_hs__a222o_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a222oi_1": _logic_module(
        "sky130_fd_sc_hs__a222oi_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a222oi_2": _logic_module(
        "sky130_fd_sc_hs__a222oi_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a311o_1": _logic_module(
        "sky130_fd_sc_hs__a311o_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a311o_2": _logic_module(
        "sky130_fd_sc_hs__a311o_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a311o_4": _logic_module(
        "sky130_fd_sc_hs__a311o_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a311oi_1": _logic_module(
        "sky130_fd_sc_hs__a311oi_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a311oi_2": _logic_module(
        "sky130_fd_sc_hs__a311oi_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a311oi_4": _logic_module(
        "sky130_fd_sc_hs__a311oi_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a2111o_1": _logic_module(
        "sky130_fd_sc_hs__a2111o_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a2111o_2": _logic_module(
        "sky130_fd_sc_hs__a2111o_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a2111o_4": _logic_module(
        "sky130_fd_sc_hs__a2111o_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__a2111oi_1": _logic_module(
        "sky130_fd_sc_hs__a2111oi_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a2111oi_2": _logic_module(
        "sky130_fd_sc_hs__a2111oi_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__a2111oi_4": _logic_module(
        "sky130_fd_sc_hs__a2111oi_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__and2_1": _logic_module(
        "sky130_fd_sc_hs__and2_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and2_2": _logic_module(
        "sky130_fd_sc_hs__and2_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and2_4": _logic_module(
        "sky130_fd_sc_hs__and2_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and2b_1": _logic_module(
        "sky130_fd_sc_hs__and2b_1",
        "High Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and2b_2": _logic_module(
        "sky130_fd_sc_hs__and2b_2",
        "High Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and2b_4": _logic_module(
        "sky130_fd_sc_hs__and2b_4",
        "High Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and3_1": _logic_module(
        "sky130_fd_sc_hs__and3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and3_2": _logic_module(
        "sky130_fd_sc_hs__and3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and3_4": _logic_module(
        "sky130_fd_sc_hs__and3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and3b_1": _logic_module(
        "sky130_fd_sc_hs__and3b_1",
        "High Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and3b_2": _logic_module(
        "sky130_fd_sc_hs__and3b_2",
        "High Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and3b_4": _logic_module(
        "sky130_fd_sc_hs__and3b_4",
        "High Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4_1": _logic_module(
        "sky130_fd_sc_hs__and4_1",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4_2": _logic_module(
        "sky130_fd_sc_hs__and4_2",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4_4": _logic_module(
        "sky130_fd_sc_hs__and4_4",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4b_1": _logic_module(
        "sky130_fd_sc_hs__and4b_1",
        "High Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4b_2": _logic_module(
        "sky130_fd_sc_hs__and4b_2",
        "High Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4b_4": _logic_module(
        "sky130_fd_sc_hs__and4b_4",
        "High Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4bb_1": _logic_module(
        "sky130_fd_sc_hs__and4bb_1",
        "High Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4bb_2": _logic_module(
        "sky130_fd_sc_hs__and4bb_2",
        "High Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__and4bb_4": _logic_module(
        "sky130_fd_sc_hs__and4bb_4",
        "High Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__buf_1": _logic_module(
        "sky130_fd_sc_hs__buf_1", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_hs__buf_2": _logic_module(
        "sky130_fd_sc_hs__buf_2", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_hs__buf_4": _logic_module(
        "sky130_fd_sc_hs__buf_4", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_hs__buf_8": _logic_module(
        "sky130_fd_sc_hs__buf_8", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_hs__buf_16": _logic_module(
        "sky130_fd_sc_hs__buf_16",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__bufbuf_8": _logic_module(
        "sky130_fd_sc_hs__bufbuf_8",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__bufbuf_16": _logic_module(
        "sky130_fd_sc_hs__bufbuf_16",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__bufinv_8": _logic_module(
        "sky130_fd_sc_hs__bufinv_8",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__bufinv_16": _logic_module(
        "sky130_fd_sc_hs__bufinv_16",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkbuf_1": _logic_module(
        "sky130_fd_sc_hs__clkbuf_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__clkbuf_2": _logic_module(
        "sky130_fd_sc_hs__clkbuf_2",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__clkbuf_4": _logic_module(
        "sky130_fd_sc_hs__clkbuf_4",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__clkbuf_8": _logic_module(
        "sky130_fd_sc_hs__clkbuf_8",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__clkbuf_16": _logic_module(
        "sky130_fd_sc_hs__clkbuf_16",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__clkdlyinv3sd1_1": _logic_module(
        "sky130_fd_sc_hs__clkdlyinv3sd1_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkdlyinv3sd2_1": _logic_module(
        "sky130_fd_sc_hs__clkdlyinv3sd2_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkdlyinv3sd3_1": _logic_module(
        "sky130_fd_sc_hs__clkdlyinv3sd3_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkdlyinv5sd1_1": _logic_module(
        "sky130_fd_sc_hs__clkdlyinv5sd1_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkdlyinv5sd2_1": _logic_module(
        "sky130_fd_sc_hs__clkdlyinv5sd2_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkdlyinv5sd3_1": _logic_module(
        "sky130_fd_sc_hs__clkdlyinv5sd3_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkinv_1": _logic_module(
        "sky130_fd_sc_hs__clkinv_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkinv_2": _logic_module(
        "sky130_fd_sc_hs__clkinv_2",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkinv_4": _logic_module(
        "sky130_fd_sc_hs__clkinv_4",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkinv_8": _logic_module(
        "sky130_fd_sc_hs__clkinv_8",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__clkinv_16": _logic_module(
        "sky130_fd_sc_hs__clkinv_16",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__conb_1": _logic_module(
        "sky130_fd_sc_hs__conb_1",
        "High Speed",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_hs__decap_4": _logic_module(
        "sky130_fd_sc_hs__decap_4", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__decap_8": _logic_module(
        "sky130_fd_sc_hs__decap_8", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__dfbbn_1": _logic_module(
        "sky130_fd_sc_hs__dfbbn_1",
        "High Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfbbn_2": _logic_module(
        "sky130_fd_sc_hs__dfbbn_2",
        "High Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfbbp_1": _logic_module(
        "sky130_fd_sc_hs__dfbbp_1",
        "High Speed",
        ["CLK", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfrbp_1": _logic_module(
        "sky130_fd_sc_hs__dfrbp_1",
        "High Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfrbp_2": _logic_module(
        "sky130_fd_sc_hs__dfrbp_2",
        "High Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfrtn_1": _logic_module(
        "sky130_fd_sc_hs__dfrtn_1",
        "High Speed",
        ["CLK_N", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfrtp_1": _logic_module(
        "sky130_fd_sc_hs__dfrtp_1",
        "High Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfrtp_2": _logic_module(
        "sky130_fd_sc_hs__dfrtp_2",
        "High Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfrtp_4": _logic_module(
        "sky130_fd_sc_hs__dfrtp_4",
        "High Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfsbp_1": _logic_module(
        "sky130_fd_sc_hs__dfsbp_1",
        "High Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfsbp_2": _logic_module(
        "sky130_fd_sc_hs__dfsbp_2",
        "High Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfstp_1": _logic_module(
        "sky130_fd_sc_hs__dfstp_1",
        "High Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfstp_2": _logic_module(
        "sky130_fd_sc_hs__dfstp_2",
        "High Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfstp_4": _logic_module(
        "sky130_fd_sc_hs__dfstp_4",
        "High Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfxbp_1": _logic_module(
        "sky130_fd_sc_hs__dfxbp_1",
        "High Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfxbp_2": _logic_module(
        "sky130_fd_sc_hs__dfxbp_2",
        "High Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dfxtp_1": _logic_module(
        "sky130_fd_sc_hs__dfxtp_1",
        "High Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfxtp_2": _logic_module(
        "sky130_fd_sc_hs__dfxtp_2",
        "High Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dfxtp_4": _logic_module(
        "sky130_fd_sc_hs__dfxtp_4",
        "High Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__diode_2": _logic_module(
        "sky130_fd_sc_hs__diode_2",
        "High Speed",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hs__dlclkp_1": _logic_module(
        "sky130_fd_sc_hs__dlclkp_1",
        "High Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hs__dlclkp_2": _logic_module(
        "sky130_fd_sc_hs__dlclkp_2",
        "High Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hs__dlclkp_4": _logic_module(
        "sky130_fd_sc_hs__dlclkp_4",
        "High Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hs__dlrbn_1": _logic_module(
        "sky130_fd_sc_hs__dlrbn_1",
        "High Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlrbn_2": _logic_module(
        "sky130_fd_sc_hs__dlrbn_2",
        "High Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlrbp_1": _logic_module(
        "sky130_fd_sc_hs__dlrbp_1",
        "High Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlrbp_2": _logic_module(
        "sky130_fd_sc_hs__dlrbp_2",
        "High Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlrtn_1": _logic_module(
        "sky130_fd_sc_hs__dlrtn_1",
        "High Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlrtn_2": _logic_module(
        "sky130_fd_sc_hs__dlrtn_2",
        "High Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlrtn_4": _logic_module(
        "sky130_fd_sc_hs__dlrtn_4",
        "High Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlrtp_1": _logic_module(
        "sky130_fd_sc_hs__dlrtp_1",
        "High Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlrtp_2": _logic_module(
        "sky130_fd_sc_hs__dlrtp_2",
        "High Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlrtp_4": _logic_module(
        "sky130_fd_sc_hs__dlrtp_4",
        "High Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlxbn_1": _logic_module(
        "sky130_fd_sc_hs__dlxbn_1",
        "High Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlxbn_2": _logic_module(
        "sky130_fd_sc_hs__dlxbn_2",
        "High Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlxbp_1": _logic_module(
        "sky130_fd_sc_hs__dlxbp_1",
        "High Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__dlxtn_1": _logic_module(
        "sky130_fd_sc_hs__dlxtn_1",
        "High Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlxtn_2": _logic_module(
        "sky130_fd_sc_hs__dlxtn_2",
        "High Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlxtn_4": _logic_module(
        "sky130_fd_sc_hs__dlxtn_4",
        "High Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlxtp_1": _logic_module(
        "sky130_fd_sc_hs__dlxtp_1",
        "High Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__dlygate4sd1_1": _logic_module(
        "sky130_fd_sc_hs__dlygate4sd1_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__dlygate4sd2_1": _logic_module(
        "sky130_fd_sc_hs__dlygate4sd2_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__dlygate4sd3_1": _logic_module(
        "sky130_fd_sc_hs__dlygate4sd3_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__dlymetal6s2s_1": _logic_module(
        "sky130_fd_sc_hs__dlymetal6s2s_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__dlymetal6s4s_1": _logic_module(
        "sky130_fd_sc_hs__dlymetal6s4s_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__dlymetal6s6s_1": _logic_module(
        "sky130_fd_sc_hs__dlymetal6s6s_1",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__ebufn_1": _logic_module(
        "sky130_fd_sc_hs__ebufn_1",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__ebufn_2": _logic_module(
        "sky130_fd_sc_hs__ebufn_2",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__ebufn_4": _logic_module(
        "sky130_fd_sc_hs__ebufn_4",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__ebufn_8": _logic_module(
        "sky130_fd_sc_hs__ebufn_8",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__edfxbp_1": _logic_module(
        "sky130_fd_sc_hs__edfxbp_1",
        "High Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__edfxtp_1": _logic_module(
        "sky130_fd_sc_hs__edfxtp_1",
        "High Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__einvn_1": _logic_module(
        "sky130_fd_sc_hs__einvn_1",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvn_2": _logic_module(
        "sky130_fd_sc_hs__einvn_2",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvn_4": _logic_module(
        "sky130_fd_sc_hs__einvn_4",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvn_8": _logic_module(
        "sky130_fd_sc_hs__einvn_8",
        "High Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvp_1": _logic_module(
        "sky130_fd_sc_hs__einvp_1",
        "High Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvp_2": _logic_module(
        "sky130_fd_sc_hs__einvp_2",
        "High Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvp_4": _logic_module(
        "sky130_fd_sc_hs__einvp_4",
        "High Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__einvp_8": _logic_module(
        "sky130_fd_sc_hs__einvp_8",
        "High Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hs__fa_1": _logic_module(
        "sky130_fd_sc_hs__fa_1",
        "High Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fa_2": _logic_module(
        "sky130_fd_sc_hs__fa_2",
        "High Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fa_4": _logic_module(
        "sky130_fd_sc_hs__fa_4",
        "High Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fah_1": _logic_module(
        "sky130_fd_sc_hs__fah_1",
        "High Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fah_2": _logic_module(
        "sky130_fd_sc_hs__fah_2",
        "High Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fah_4": _logic_module(
        "sky130_fd_sc_hs__fah_4",
        "High Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fahcin_1": _logic_module(
        "sky130_fd_sc_hs__fahcin_1",
        "High Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__fahcon_1": _logic_module(
        "sky130_fd_sc_hs__fahcon_1",
        "High Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT_N", "SUM"],
    ),
    "sky130_fd_sc_hs__fill_1": _logic_module(
        "sky130_fd_sc_hs__fill_1", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__fill_2": _logic_module(
        "sky130_fd_sc_hs__fill_2", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__fill_4": _logic_module(
        "sky130_fd_sc_hs__fill_4", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__fill_8": _logic_module(
        "sky130_fd_sc_hs__fill_8", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__fill_diode_2": _logic_module(
        "sky130_fd_sc_hs__fill_diode_2", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__fill_diode_4": _logic_module(
        "sky130_fd_sc_hs__fill_diode_4", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__fill_diode_8": _logic_module(
        "sky130_fd_sc_hs__fill_diode_8", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__ha_1": _logic_module(
        "sky130_fd_sc_hs__ha_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__ha_2": _logic_module(
        "sky130_fd_sc_hs__ha_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__ha_4": _logic_module(
        "sky130_fd_sc_hs__ha_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_hs__inv_1": _logic_module(
        "sky130_fd_sc_hs__inv_1", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_hs__inv_2": _logic_module(
        "sky130_fd_sc_hs__inv_2", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_hs__inv_4": _logic_module(
        "sky130_fd_sc_hs__inv_4", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_hs__inv_8": _logic_module(
        "sky130_fd_sc_hs__inv_8", "High Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_hs__inv_16": _logic_module(
        "sky130_fd_sc_hs__inv_16",
        "High Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__maj3_1": _logic_module(
        "sky130_fd_sc_hs__maj3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__maj3_2": _logic_module(
        "sky130_fd_sc_hs__maj3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__maj3_4": _logic_module(
        "sky130_fd_sc_hs__maj3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__mux2_1": _logic_module(
        "sky130_fd_sc_hs__mux2_1",
        "High Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__mux2_2": _logic_module(
        "sky130_fd_sc_hs__mux2_2",
        "High Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__mux2_4": _logic_module(
        "sky130_fd_sc_hs__mux2_4",
        "High Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__mux2i_1": _logic_module(
        "sky130_fd_sc_hs__mux2i_1",
        "High Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__mux2i_2": _logic_module(
        "sky130_fd_sc_hs__mux2i_2",
        "High Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__mux2i_4": _logic_module(
        "sky130_fd_sc_hs__mux2i_4",
        "High Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__mux4_1": _logic_module(
        "sky130_fd_sc_hs__mux4_1",
        "High Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__mux4_2": _logic_module(
        "sky130_fd_sc_hs__mux4_2",
        "High Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__mux4_4": _logic_module(
        "sky130_fd_sc_hs__mux4_4",
        "High Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__nand2_1": _logic_module(
        "sky130_fd_sc_hs__nand2_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand2_2": _logic_module(
        "sky130_fd_sc_hs__nand2_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand2_4": _logic_module(
        "sky130_fd_sc_hs__nand2_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand2_8": _logic_module(
        "sky130_fd_sc_hs__nand2_8",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand2b_1": _logic_module(
        "sky130_fd_sc_hs__nand2b_1",
        "High Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand2b_2": _logic_module(
        "sky130_fd_sc_hs__nand2b_2",
        "High Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand2b_4": _logic_module(
        "sky130_fd_sc_hs__nand2b_4",
        "High Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand3_1": _logic_module(
        "sky130_fd_sc_hs__nand3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand3_2": _logic_module(
        "sky130_fd_sc_hs__nand3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand3_4": _logic_module(
        "sky130_fd_sc_hs__nand3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand3b_1": _logic_module(
        "sky130_fd_sc_hs__nand3b_1",
        "High Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand3b_2": _logic_module(
        "sky130_fd_sc_hs__nand3b_2",
        "High Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand3b_4": _logic_module(
        "sky130_fd_sc_hs__nand3b_4",
        "High Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4_1": _logic_module(
        "sky130_fd_sc_hs__nand4_1",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4_2": _logic_module(
        "sky130_fd_sc_hs__nand4_2",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4_4": _logic_module(
        "sky130_fd_sc_hs__nand4_4",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4b_1": _logic_module(
        "sky130_fd_sc_hs__nand4b_1",
        "High Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4b_2": _logic_module(
        "sky130_fd_sc_hs__nand4b_2",
        "High Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4b_4": _logic_module(
        "sky130_fd_sc_hs__nand4b_4",
        "High Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4bb_1": _logic_module(
        "sky130_fd_sc_hs__nand4bb_1",
        "High Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4bb_2": _logic_module(
        "sky130_fd_sc_hs__nand4bb_2",
        "High Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nand4bb_4": _logic_module(
        "sky130_fd_sc_hs__nand4bb_4",
        "High Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2_1": _logic_module(
        "sky130_fd_sc_hs__nor2_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2_2": _logic_module(
        "sky130_fd_sc_hs__nor2_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2_4": _logic_module(
        "sky130_fd_sc_hs__nor2_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2_8": _logic_module(
        "sky130_fd_sc_hs__nor2_8",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2b_1": _logic_module(
        "sky130_fd_sc_hs__nor2b_1",
        "High Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2b_2": _logic_module(
        "sky130_fd_sc_hs__nor2b_2",
        "High Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor2b_4": _logic_module(
        "sky130_fd_sc_hs__nor2b_4",
        "High Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor3_1": _logic_module(
        "sky130_fd_sc_hs__nor3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor3_2": _logic_module(
        "sky130_fd_sc_hs__nor3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor3_4": _logic_module(
        "sky130_fd_sc_hs__nor3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor3b_1": _logic_module(
        "sky130_fd_sc_hs__nor3b_1",
        "High Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor3b_2": _logic_module(
        "sky130_fd_sc_hs__nor3b_2",
        "High Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor3b_4": _logic_module(
        "sky130_fd_sc_hs__nor3b_4",
        "High Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4_1": _logic_module(
        "sky130_fd_sc_hs__nor4_1",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4_2": _logic_module(
        "sky130_fd_sc_hs__nor4_2",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4_4": _logic_module(
        "sky130_fd_sc_hs__nor4_4",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4b_1": _logic_module(
        "sky130_fd_sc_hs__nor4b_1",
        "High Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4b_2": _logic_module(
        "sky130_fd_sc_hs__nor4b_2",
        "High Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4b_4": _logic_module(
        "sky130_fd_sc_hs__nor4b_4",
        "High Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4bb_1": _logic_module(
        "sky130_fd_sc_hs__nor4bb_1",
        "High Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4bb_2": _logic_module(
        "sky130_fd_sc_hs__nor4bb_2",
        "High Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__nor4bb_4": _logic_module(
        "sky130_fd_sc_hs__nor4bb_4",
        "High Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o2bb2a_1": _logic_module(
        "sky130_fd_sc_hs__o2bb2a_1",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o2bb2a_2": _logic_module(
        "sky130_fd_sc_hs__o2bb2a_2",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o2bb2a_4": _logic_module(
        "sky130_fd_sc_hs__o2bb2a_4",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o2bb2ai_1": _logic_module(
        "sky130_fd_sc_hs__o2bb2ai_1",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o2bb2ai_2": _logic_module(
        "sky130_fd_sc_hs__o2bb2ai_2",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o2bb2ai_4": _logic_module(
        "sky130_fd_sc_hs__o2bb2ai_4",
        "High Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o21a_1": _logic_module(
        "sky130_fd_sc_hs__o21a_1",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o21a_2": _logic_module(
        "sky130_fd_sc_hs__o21a_2",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o21a_4": _logic_module(
        "sky130_fd_sc_hs__o21a_4",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o21ai_1": _logic_module(
        "sky130_fd_sc_hs__o21ai_1",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o21ai_2": _logic_module(
        "sky130_fd_sc_hs__o21ai_2",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o21ai_4": _logic_module(
        "sky130_fd_sc_hs__o21ai_4",
        "High Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o21ba_1": _logic_module(
        "sky130_fd_sc_hs__o21ba_1",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o21ba_2": _logic_module(
        "sky130_fd_sc_hs__o21ba_2",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o21ba_4": _logic_module(
        "sky130_fd_sc_hs__o21ba_4",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o21bai_1": _logic_module(
        "sky130_fd_sc_hs__o21bai_1",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o21bai_2": _logic_module(
        "sky130_fd_sc_hs__o21bai_2",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o21bai_4": _logic_module(
        "sky130_fd_sc_hs__o21bai_4",
        "High Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o22a_1": _logic_module(
        "sky130_fd_sc_hs__o22a_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o22a_2": _logic_module(
        "sky130_fd_sc_hs__o22a_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o22a_4": _logic_module(
        "sky130_fd_sc_hs__o22a_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o22ai_1": _logic_module(
        "sky130_fd_sc_hs__o22ai_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o22ai_2": _logic_module(
        "sky130_fd_sc_hs__o22ai_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o22ai_4": _logic_module(
        "sky130_fd_sc_hs__o22ai_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o31a_1": _logic_module(
        "sky130_fd_sc_hs__o31a_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o31a_2": _logic_module(
        "sky130_fd_sc_hs__o31a_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o31a_4": _logic_module(
        "sky130_fd_sc_hs__o31a_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o31ai_1": _logic_module(
        "sky130_fd_sc_hs__o31ai_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o31ai_2": _logic_module(
        "sky130_fd_sc_hs__o31ai_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o31ai_4": _logic_module(
        "sky130_fd_sc_hs__o31ai_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o32a_1": _logic_module(
        "sky130_fd_sc_hs__o32a_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o32a_2": _logic_module(
        "sky130_fd_sc_hs__o32a_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o32a_4": _logic_module(
        "sky130_fd_sc_hs__o32a_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o32ai_1": _logic_module(
        "sky130_fd_sc_hs__o32ai_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o32ai_2": _logic_module(
        "sky130_fd_sc_hs__o32ai_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o32ai_4": _logic_module(
        "sky130_fd_sc_hs__o32ai_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o41a_1": _logic_module(
        "sky130_fd_sc_hs__o41a_1",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o41a_2": _logic_module(
        "sky130_fd_sc_hs__o41a_2",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o41a_4": _logic_module(
        "sky130_fd_sc_hs__o41a_4",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o41ai_1": _logic_module(
        "sky130_fd_sc_hs__o41ai_1",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o41ai_2": _logic_module(
        "sky130_fd_sc_hs__o41ai_2",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o41ai_4": _logic_module(
        "sky130_fd_sc_hs__o41ai_4",
        "High Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o211a_1": _logic_module(
        "sky130_fd_sc_hs__o211a_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o211a_2": _logic_module(
        "sky130_fd_sc_hs__o211a_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o211a_4": _logic_module(
        "sky130_fd_sc_hs__o211a_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o211ai_1": _logic_module(
        "sky130_fd_sc_hs__o211ai_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o211ai_2": _logic_module(
        "sky130_fd_sc_hs__o211ai_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o211ai_4": _logic_module(
        "sky130_fd_sc_hs__o211ai_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o221a_1": _logic_module(
        "sky130_fd_sc_hs__o221a_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o221a_2": _logic_module(
        "sky130_fd_sc_hs__o221a_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o221a_4": _logic_module(
        "sky130_fd_sc_hs__o221a_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o221ai_1": _logic_module(
        "sky130_fd_sc_hs__o221ai_1",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o221ai_2": _logic_module(
        "sky130_fd_sc_hs__o221ai_2",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o221ai_4": _logic_module(
        "sky130_fd_sc_hs__o221ai_4",
        "High Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o311a_1": _logic_module(
        "sky130_fd_sc_hs__o311a_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o311a_2": _logic_module(
        "sky130_fd_sc_hs__o311a_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o311a_4": _logic_module(
        "sky130_fd_sc_hs__o311a_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o311ai_1": _logic_module(
        "sky130_fd_sc_hs__o311ai_1",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o311ai_2": _logic_module(
        "sky130_fd_sc_hs__o311ai_2",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o311ai_4": _logic_module(
        "sky130_fd_sc_hs__o311ai_4",
        "High Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o2111a_1": _logic_module(
        "sky130_fd_sc_hs__o2111a_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o2111a_2": _logic_module(
        "sky130_fd_sc_hs__o2111a_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o2111a_4": _logic_module(
        "sky130_fd_sc_hs__o2111a_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__o2111ai_1": _logic_module(
        "sky130_fd_sc_hs__o2111ai_1",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o2111ai_2": _logic_module(
        "sky130_fd_sc_hs__o2111ai_2",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__o2111ai_4": _logic_module(
        "sky130_fd_sc_hs__o2111ai_4",
        "High Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__or2_1": _logic_module(
        "sky130_fd_sc_hs__or2_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or2_2": _logic_module(
        "sky130_fd_sc_hs__or2_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or2_4": _logic_module(
        "sky130_fd_sc_hs__or2_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or2b_1": _logic_module(
        "sky130_fd_sc_hs__or2b_1",
        "High Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or2b_2": _logic_module(
        "sky130_fd_sc_hs__or2b_2",
        "High Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or2b_4": _logic_module(
        "sky130_fd_sc_hs__or2b_4",
        "High Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or3_1": _logic_module(
        "sky130_fd_sc_hs__or3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or3_2": _logic_module(
        "sky130_fd_sc_hs__or3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or3_4": _logic_module(
        "sky130_fd_sc_hs__or3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or3b_1": _logic_module(
        "sky130_fd_sc_hs__or3b_1",
        "High Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or3b_2": _logic_module(
        "sky130_fd_sc_hs__or3b_2",
        "High Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or3b_4": _logic_module(
        "sky130_fd_sc_hs__or3b_4",
        "High Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4_1": _logic_module(
        "sky130_fd_sc_hs__or4_1",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4_2": _logic_module(
        "sky130_fd_sc_hs__or4_2",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4_4": _logic_module(
        "sky130_fd_sc_hs__or4_4",
        "High Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4b_1": _logic_module(
        "sky130_fd_sc_hs__or4b_1",
        "High Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4b_2": _logic_module(
        "sky130_fd_sc_hs__or4b_2",
        "High Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4b_4": _logic_module(
        "sky130_fd_sc_hs__or4b_4",
        "High Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4bb_1": _logic_module(
        "sky130_fd_sc_hs__or4bb_1",
        "High Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4bb_2": _logic_module(
        "sky130_fd_sc_hs__or4bb_2",
        "High Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__or4bb_4": _logic_module(
        "sky130_fd_sc_hs__or4bb_4",
        "High Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__sdfbbn_1": _logic_module(
        "sky130_fd_sc_hs__sdfbbn_1",
        "High Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hs__sdfbbn_2": _logic_module(
        "sky130_fd_sc_hs__sdfbbn_2",
        "High Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hs__sdfbbp_1": _logic_module(
        "sky130_fd_sc_hs__sdfbbp_1",
        "High Speed",
        [
            "CLK",
            "D",
            "RESET_B",
            "SCD",
            "SCE",
            "SET_B",
            "VGND",
            "VNB",
            "VPB",
            "VPWR",
            "Q",
        ],
    ),
    "sky130_fd_sc_hs__sdfrbp_1": _logic_module(
        "sky130_fd_sc_hs__sdfrbp_1",
        "High Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sdfrbp_2": _logic_module(
        "sky130_fd_sc_hs__sdfrbp_2",
        "High Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sdfrtn_1": _logic_module(
        "sky130_fd_sc_hs__sdfrtn_1",
        "High Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfrtp_1": _logic_module(
        "sky130_fd_sc_hs__sdfrtp_1",
        "High Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfrtp_2": _logic_module(
        "sky130_fd_sc_hs__sdfrtp_2",
        "High Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfrtp_4": _logic_module(
        "sky130_fd_sc_hs__sdfrtp_4",
        "High Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfsbp_1": _logic_module(
        "sky130_fd_sc_hs__sdfsbp_1",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sdfsbp_2": _logic_module(
        "sky130_fd_sc_hs__sdfsbp_2",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sdfstp_1": _logic_module(
        "sky130_fd_sc_hs__sdfstp_1",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfstp_2": _logic_module(
        "sky130_fd_sc_hs__sdfstp_2",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfstp_4": _logic_module(
        "sky130_fd_sc_hs__sdfstp_4",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfxbp_1": _logic_module(
        "sky130_fd_sc_hs__sdfxbp_1",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sdfxbp_2": _logic_module(
        "sky130_fd_sc_hs__sdfxbp_2",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sdfxtp_1": _logic_module(
        "sky130_fd_sc_hs__sdfxtp_1",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfxtp_2": _logic_module(
        "sky130_fd_sc_hs__sdfxtp_2",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdfxtp_4": _logic_module(
        "sky130_fd_sc_hs__sdfxtp_4",
        "High Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sdlclkp_1": _logic_module(
        "sky130_fd_sc_hs__sdlclkp_1",
        "High Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hs__sdlclkp_2": _logic_module(
        "sky130_fd_sc_hs__sdlclkp_2",
        "High Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hs__sdlclkp_4": _logic_module(
        "sky130_fd_sc_hs__sdlclkp_4",
        "High Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hs__sedfxbp_1": _logic_module(
        "sky130_fd_sc_hs__sedfxbp_1",
        "High Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sedfxbp_2": _logic_module(
        "sky130_fd_sc_hs__sedfxbp_2",
        "High Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hs__sedfxtp_1": _logic_module(
        "sky130_fd_sc_hs__sedfxtp_1",
        "High Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sedfxtp_2": _logic_module(
        "sky130_fd_sc_hs__sedfxtp_2",
        "High Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__sedfxtp_4": _logic_module(
        "sky130_fd_sc_hs__sedfxtp_4",
        "High Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hs__tap_1": _logic_module(
        "sky130_fd_sc_hs__tap_1", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__tap_2": _logic_module(
        "sky130_fd_sc_hs__tap_2", "High Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__tapmet1_2": _logic_module(
        "sky130_fd_sc_hs__tapmet1_2", "High Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__tapvgnd2_1": _logic_module(
        "sky130_fd_sc_hs__tapvgnd2_1", "High Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__tapvgnd_1": _logic_module(
        "sky130_fd_sc_hs__tapvgnd_1", "High Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hs__tapvpwrvgnd_1": _logic_module(
        "sky130_fd_sc_hs__tapvpwrvgnd_1", "High Speed", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_hs__xnor2_1": _logic_module(
        "sky130_fd_sc_hs__xnor2_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__xnor2_2": _logic_module(
        "sky130_fd_sc_hs__xnor2_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__xnor2_4": _logic_module(
        "sky130_fd_sc_hs__xnor2_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hs__xnor3_1": _logic_module(
        "sky130_fd_sc_hs__xnor3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xnor3_2": _logic_module(
        "sky130_fd_sc_hs__xnor3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xnor3_4": _logic_module(
        "sky130_fd_sc_hs__xnor3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xor2_1": _logic_module(
        "sky130_fd_sc_hs__xor2_1",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xor2_2": _logic_module(
        "sky130_fd_sc_hs__xor2_2",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xor2_4": _logic_module(
        "sky130_fd_sc_hs__xor2_4",
        "High Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xor3_1": _logic_module(
        "sky130_fd_sc_hs__xor3_1",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xor3_2": _logic_module(
        "sky130_fd_sc_hs__xor3_2",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hs__xor3_4": _logic_module(
        "sky130_fd_sc_hs__xor3_4",
        "High Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

hvl: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_hvl__a21o_1": _logic_module(
        "sky130_fd_sc_hvl__a21o_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__a21oi_1": _logic_module(
        "sky130_fd_sc_hvl__a21oi_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__a22o_1": _logic_module(
        "sky130_fd_sc_hvl__a22o_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__a22oi_1": _logic_module(
        "sky130_fd_sc_hvl__a22oi_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__and2_1": _logic_module(
        "sky130_fd_sc_hvl__and2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__and3_1": _logic_module(
        "sky130_fd_sc_hvl__and3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__buf_1": _logic_module(
        "sky130_fd_sc_hvl__buf_1",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__buf_2": _logic_module(
        "sky130_fd_sc_hvl__buf_2",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__buf_4": _logic_module(
        "sky130_fd_sc_hvl__buf_4",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__buf_8": _logic_module(
        "sky130_fd_sc_hvl__buf_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__buf_16": _logic_module(
        "sky130_fd_sc_hvl__buf_16",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__buf_32": _logic_module(
        "sky130_fd_sc_hvl__buf_32",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__conb_1": _logic_module(
        "sky130_fd_sc_hvl__conb_1",
        "High Voltage",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_hvl__decap_4": _logic_module(
        "sky130_fd_sc_hvl__decap_4", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hvl__decap_8": _logic_module(
        "sky130_fd_sc_hvl__decap_8", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hvl__dfrbp_1": _logic_module(
        "sky130_fd_sc_hvl__dfrbp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hvl__dfrtp_1": _logic_module(
        "sky130_fd_sc_hvl__dfrtp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__dfsbp_1": _logic_module(
        "sky130_fd_sc_hvl__dfsbp_1",
        "High Voltage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hvl__dfstp_1": _logic_module(
        "sky130_fd_sc_hvl__dfstp_1",
        "High Voltage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__dfxbp_1": _logic_module(
        "sky130_fd_sc_hvl__dfxbp_1",
        "High Voltage",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hvl__dfxtp_1": _logic_module(
        "sky130_fd_sc_hvl__dfxtp_1",
        "High Voltage",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__diode_2": _logic_module(
        "sky130_fd_sc_hvl__diode_2",
        "High Voltage",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hvl__dlclkp_1": _logic_module(
        "sky130_fd_sc_hvl__dlclkp_1",
        "High Voltage",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hvl__dlrtp_1": _logic_module(
        "sky130_fd_sc_hvl__dlrtp_1",
        "High Voltage",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__dlxtp_1": _logic_module(
        "sky130_fd_sc_hvl__dlxtp_1",
        "High Voltage",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__einvn_1": _logic_module(
        "sky130_fd_sc_hvl__einvn_1",
        "High Voltage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hvl__einvp_1": _logic_module(
        "sky130_fd_sc_hvl__einvp_1",
        "High Voltage",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_hvl__fill_1": _logic_module(
        "sky130_fd_sc_hvl__fill_1", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hvl__fill_2": _logic_module(
        "sky130_fd_sc_hvl__fill_2", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hvl__fill_4": _logic_module(
        "sky130_fd_sc_hvl__fill_4", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hvl__fill_8": _logic_module(
        "sky130_fd_sc_hvl__fill_8", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_hvl__inv_1": _logic_module(
        "sky130_fd_sc_hvl__inv_1",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__inv_2": _logic_module(
        "sky130_fd_sc_hvl__inv_2",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__inv_4": _logic_module(
        "sky130_fd_sc_hvl__inv_4",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__inv_8": _logic_module(
        "sky130_fd_sc_hvl__inv_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__inv_16": _logic_module(
        "sky130_fd_sc_hvl__inv_16",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__lsbufhv2hv_hl_1": _logic_module(
        "sky130_fd_sc_hvl__lsbufhv2hv_hl_1",
        "High Voltage",
        ["A", "LOWHVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__lsbufhv2hv_lh_1": _logic_module(
        "sky130_fd_sc_hvl__lsbufhv2hv_lh_1",
        "High Voltage",
        ["A", "LOWHVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__lsbufhv2lv_1": _logic_module(
        "sky130_fd_sc_hvl__lsbufhv2lv_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__lsbufhv2lv_simple_1": _logic_module(
        "sky130_fd_sc_hvl__lsbufhv2lv_simple_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__lsbuflv2hv_1": _logic_module(
        "sky130_fd_sc_hvl__lsbuflv2hv_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__lsbuflv2hv_clkiso_hlkg_3": _logic_module(
        "sky130_fd_sc_hvl__lsbuflv2hv_clkiso_hlkg_3",
        "High Voltage",
        ["A", "SLEEP_B", "LVPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hvl__lsbuflv2hv_isosrchvaon_1": _logic_module(
        "sky130_fd_sc_hvl__lsbuflv2hv_isosrchvaon_1",
        "High Voltage",
        ["A", "SLEEP_B", "LVPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_hvl__lsbuflv2hv_symmetric_1": _logic_module(
        "sky130_fd_sc_hvl__lsbuflv2hv_symmetric_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__mux2_1": _logic_module(
        "sky130_fd_sc_hvl__mux2_1",
        "High Voltage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__mux4_1": _logic_module(
        "sky130_fd_sc_hvl__mux4_1",
        "High Voltage",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__nand2_1": _logic_module(
        "sky130_fd_sc_hvl__nand2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__nand3_1": _logic_module(
        "sky130_fd_sc_hvl__nand3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__nor2_1": _logic_module(
        "sky130_fd_sc_hvl__nor2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__nor3_1": _logic_module(
        "sky130_fd_sc_hvl__nor3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__o21a_1": _logic_module(
        "sky130_fd_sc_hvl__o21a_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__o21ai_1": _logic_module(
        "sky130_fd_sc_hvl__o21ai_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__o22a_1": _logic_module(
        "sky130_fd_sc_hvl__o22a_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__o22ai_1": _logic_module(
        "sky130_fd_sc_hvl__o22ai_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__or2_1": _logic_module(
        "sky130_fd_sc_hvl__or2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__or3_1": _logic_module(
        "sky130_fd_sc_hvl__or3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__probe_p_8": _logic_module(
        "sky130_fd_sc_hvl__probe_p_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__probec_p_8": _logic_module(
        "sky130_fd_sc_hvl__probec_p_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__schmittbuf_1": _logic_module(
        "sky130_fd_sc_hvl__schmittbuf_1",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_hvl__sdfrbp_1": _logic_module(
        "sky130_fd_sc_hvl__sdfrbp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hvl__sdfrtp_1": _logic_module(
        "sky130_fd_sc_hvl__sdfrtp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__sdfsbp_1": _logic_module(
        "sky130_fd_sc_hvl__sdfsbp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hvl__sdfstp_1": _logic_module(
        "sky130_fd_sc_hvl__sdfstp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__sdfxbp_1": _logic_module(
        "sky130_fd_sc_hvl__sdfxbp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_hvl__sdfxtp_1": _logic_module(
        "sky130_fd_sc_hvl__sdfxtp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__sdlclkp_1": _logic_module(
        "sky130_fd_sc_hvl__sdlclkp_1",
        "High Voltage",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_hvl__sdlxtp_1": _logic_module(
        "sky130_fd_sc_hvl__sdlxtp_1",
        "High Voltage",
        ["D", "GATE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_hvl__xnor2_1": _logic_module(
        "sky130_fd_sc_hvl__xnor2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_hvl__xor2_1": _logic_module(
        "sky130_fd_sc_hvl__xor2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

lp: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_lp__a2bb2o_0": _logic_module(
        "sky130_fd_sc_lp__a2bb2o_0",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2bb2o_1": _logic_module(
        "sky130_fd_sc_lp__a2bb2o_1",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2bb2o_2": _logic_module(
        "sky130_fd_sc_lp__a2bb2o_2",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2bb2o_4": _logic_module(
        "sky130_fd_sc_lp__a2bb2o_4",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2bb2o_lp": _logic_module(
        "sky130_fd_sc_lp__a2bb2o_lp",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2bb2o_m": _logic_module(
        "sky130_fd_sc_lp__a2bb2o_m",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2bb2oi_0": _logic_module(
        "sky130_fd_sc_lp__a2bb2oi_0",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2bb2oi_1": _logic_module(
        "sky130_fd_sc_lp__a2bb2oi_1",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2bb2oi_2": _logic_module(
        "sky130_fd_sc_lp__a2bb2oi_2",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2bb2oi_4": _logic_module(
        "sky130_fd_sc_lp__a2bb2oi_4",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2bb2oi_lp": _logic_module(
        "sky130_fd_sc_lp__a2bb2oi_lp",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2bb2oi_m": _logic_module(
        "sky130_fd_sc_lp__a2bb2oi_m",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21bo_0": _logic_module(
        "sky130_fd_sc_lp__a21bo_0",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21bo_1": _logic_module(
        "sky130_fd_sc_lp__a21bo_1",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21bo_2": _logic_module(
        "sky130_fd_sc_lp__a21bo_2",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21bo_4": _logic_module(
        "sky130_fd_sc_lp__a21bo_4",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21bo_lp": _logic_module(
        "sky130_fd_sc_lp__a21bo_lp",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21bo_m": _logic_module(
        "sky130_fd_sc_lp__a21bo_m",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21boi_0": _logic_module(
        "sky130_fd_sc_lp__a21boi_0",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21boi_1": _logic_module(
        "sky130_fd_sc_lp__a21boi_1",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21boi_2": _logic_module(
        "sky130_fd_sc_lp__a21boi_2",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21boi_4": _logic_module(
        "sky130_fd_sc_lp__a21boi_4",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21boi_lp": _logic_module(
        "sky130_fd_sc_lp__a21boi_lp",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21boi_m": _logic_module(
        "sky130_fd_sc_lp__a21boi_m",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21o_0": _logic_module(
        "sky130_fd_sc_lp__a21o_0",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21o_1": _logic_module(
        "sky130_fd_sc_lp__a21o_1",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21o_2": _logic_module(
        "sky130_fd_sc_lp__a21o_2",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21o_4": _logic_module(
        "sky130_fd_sc_lp__a21o_4",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21o_lp": _logic_module(
        "sky130_fd_sc_lp__a21o_lp",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21o_m": _logic_module(
        "sky130_fd_sc_lp__a21o_m",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a21oi_0": _logic_module(
        "sky130_fd_sc_lp__a21oi_0",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21oi_1": _logic_module(
        "sky130_fd_sc_lp__a21oi_1",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21oi_2": _logic_module(
        "sky130_fd_sc_lp__a21oi_2",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21oi_4": _logic_module(
        "sky130_fd_sc_lp__a21oi_4",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21oi_lp": _logic_module(
        "sky130_fd_sc_lp__a21oi_lp",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a21oi_m": _logic_module(
        "sky130_fd_sc_lp__a21oi_m",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a22o_0": _logic_module(
        "sky130_fd_sc_lp__a22o_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a22o_1": _logic_module(
        "sky130_fd_sc_lp__a22o_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a22o_2": _logic_module(
        "sky130_fd_sc_lp__a22o_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a22o_4": _logic_module(
        "sky130_fd_sc_lp__a22o_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a22o_lp": _logic_module(
        "sky130_fd_sc_lp__a22o_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a22o_m": _logic_module(
        "sky130_fd_sc_lp__a22o_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a22oi_0": _logic_module(
        "sky130_fd_sc_lp__a22oi_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a22oi_1": _logic_module(
        "sky130_fd_sc_lp__a22oi_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a22oi_2": _logic_module(
        "sky130_fd_sc_lp__a22oi_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a22oi_4": _logic_module(
        "sky130_fd_sc_lp__a22oi_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a22oi_lp": _logic_module(
        "sky130_fd_sc_lp__a22oi_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a22oi_m": _logic_module(
        "sky130_fd_sc_lp__a22oi_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a31o_0": _logic_module(
        "sky130_fd_sc_lp__a31o_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a31o_1": _logic_module(
        "sky130_fd_sc_lp__a31o_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a31o_2": _logic_module(
        "sky130_fd_sc_lp__a31o_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a31o_4": _logic_module(
        "sky130_fd_sc_lp__a31o_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a31o_lp": _logic_module(
        "sky130_fd_sc_lp__a31o_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a31o_m": _logic_module(
        "sky130_fd_sc_lp__a31o_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a31oi_0": _logic_module(
        "sky130_fd_sc_lp__a31oi_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a31oi_1": _logic_module(
        "sky130_fd_sc_lp__a31oi_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a31oi_2": _logic_module(
        "sky130_fd_sc_lp__a31oi_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a31oi_4": _logic_module(
        "sky130_fd_sc_lp__a31oi_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a31oi_lp": _logic_module(
        "sky130_fd_sc_lp__a31oi_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a31oi_m": _logic_module(
        "sky130_fd_sc_lp__a31oi_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a32o_0": _logic_module(
        "sky130_fd_sc_lp__a32o_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a32o_1": _logic_module(
        "sky130_fd_sc_lp__a32o_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a32o_2": _logic_module(
        "sky130_fd_sc_lp__a32o_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a32o_4": _logic_module(
        "sky130_fd_sc_lp__a32o_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a32o_lp": _logic_module(
        "sky130_fd_sc_lp__a32o_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a32o_m": _logic_module(
        "sky130_fd_sc_lp__a32o_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a32oi_0": _logic_module(
        "sky130_fd_sc_lp__a32oi_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a32oi_1": _logic_module(
        "sky130_fd_sc_lp__a32oi_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a32oi_2": _logic_module(
        "sky130_fd_sc_lp__a32oi_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a32oi_4": _logic_module(
        "sky130_fd_sc_lp__a32oi_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a32oi_lp": _logic_module(
        "sky130_fd_sc_lp__a32oi_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a32oi_m": _logic_module(
        "sky130_fd_sc_lp__a32oi_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a41o_0": _logic_module(
        "sky130_fd_sc_lp__a41o_0",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a41o_1": _logic_module(
        "sky130_fd_sc_lp__a41o_1",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a41o_2": _logic_module(
        "sky130_fd_sc_lp__a41o_2",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a41o_4": _logic_module(
        "sky130_fd_sc_lp__a41o_4",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a41o_lp": _logic_module(
        "sky130_fd_sc_lp__a41o_lp",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a41o_m": _logic_module(
        "sky130_fd_sc_lp__a41o_m",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a41oi_0": _logic_module(
        "sky130_fd_sc_lp__a41oi_0",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a41oi_1": _logic_module(
        "sky130_fd_sc_lp__a41oi_1",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a41oi_2": _logic_module(
        "sky130_fd_sc_lp__a41oi_2",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a41oi_4": _logic_module(
        "sky130_fd_sc_lp__a41oi_4",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a41oi_lp": _logic_module(
        "sky130_fd_sc_lp__a41oi_lp",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a41oi_m": _logic_module(
        "sky130_fd_sc_lp__a41oi_m",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a211o_0": _logic_module(
        "sky130_fd_sc_lp__a211o_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a211o_1": _logic_module(
        "sky130_fd_sc_lp__a211o_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a211o_2": _logic_module(
        "sky130_fd_sc_lp__a211o_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a211o_4": _logic_module(
        "sky130_fd_sc_lp__a211o_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a211o_lp": _logic_module(
        "sky130_fd_sc_lp__a211o_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a211o_m": _logic_module(
        "sky130_fd_sc_lp__a211o_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a211oi_0": _logic_module(
        "sky130_fd_sc_lp__a211oi_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a211oi_1": _logic_module(
        "sky130_fd_sc_lp__a211oi_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a211oi_2": _logic_module(
        "sky130_fd_sc_lp__a211oi_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a211oi_4": _logic_module(
        "sky130_fd_sc_lp__a211oi_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a211oi_lp": _logic_module(
        "sky130_fd_sc_lp__a211oi_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a211oi_m": _logic_module(
        "sky130_fd_sc_lp__a211oi_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a221o_0": _logic_module(
        "sky130_fd_sc_lp__a221o_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a221o_1": _logic_module(
        "sky130_fd_sc_lp__a221o_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a221o_2": _logic_module(
        "sky130_fd_sc_lp__a221o_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a221o_4": _logic_module(
        "sky130_fd_sc_lp__a221o_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a221o_lp": _logic_module(
        "sky130_fd_sc_lp__a221o_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a221o_m": _logic_module(
        "sky130_fd_sc_lp__a221o_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a221oi_0": _logic_module(
        "sky130_fd_sc_lp__a221oi_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a221oi_1": _logic_module(
        "sky130_fd_sc_lp__a221oi_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a221oi_2": _logic_module(
        "sky130_fd_sc_lp__a221oi_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a221oi_4": _logic_module(
        "sky130_fd_sc_lp__a221oi_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a221oi_lp": _logic_module(
        "sky130_fd_sc_lp__a221oi_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a221oi_m": _logic_module(
        "sky130_fd_sc_lp__a221oi_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a311o_0": _logic_module(
        "sky130_fd_sc_lp__a311o_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a311o_1": _logic_module(
        "sky130_fd_sc_lp__a311o_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a311o_2": _logic_module(
        "sky130_fd_sc_lp__a311o_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a311o_4": _logic_module(
        "sky130_fd_sc_lp__a311o_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a311o_lp": _logic_module(
        "sky130_fd_sc_lp__a311o_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a311o_m": _logic_module(
        "sky130_fd_sc_lp__a311o_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a311oi_0": _logic_module(
        "sky130_fd_sc_lp__a311oi_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a311oi_1": _logic_module(
        "sky130_fd_sc_lp__a311oi_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a311oi_2": _logic_module(
        "sky130_fd_sc_lp__a311oi_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a311oi_4": _logic_module(
        "sky130_fd_sc_lp__a311oi_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a311oi_lp": _logic_module(
        "sky130_fd_sc_lp__a311oi_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a311oi_m": _logic_module(
        "sky130_fd_sc_lp__a311oi_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2111o_0": _logic_module(
        "sky130_fd_sc_lp__a2111o_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2111o_1": _logic_module(
        "sky130_fd_sc_lp__a2111o_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2111o_2": _logic_module(
        "sky130_fd_sc_lp__a2111o_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2111o_4": _logic_module(
        "sky130_fd_sc_lp__a2111o_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2111o_lp": _logic_module(
        "sky130_fd_sc_lp__a2111o_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2111o_m": _logic_module(
        "sky130_fd_sc_lp__a2111o_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__a2111oi_0": _logic_module(
        "sky130_fd_sc_lp__a2111oi_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2111oi_1": _logic_module(
        "sky130_fd_sc_lp__a2111oi_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2111oi_2": _logic_module(
        "sky130_fd_sc_lp__a2111oi_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2111oi_4": _logic_module(
        "sky130_fd_sc_lp__a2111oi_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2111oi_lp": _logic_module(
        "sky130_fd_sc_lp__a2111oi_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__a2111oi_m": _logic_module(
        "sky130_fd_sc_lp__a2111oi_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__and2_0": _logic_module(
        "sky130_fd_sc_lp__and2_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2_1": _logic_module(
        "sky130_fd_sc_lp__and2_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2_2": _logic_module(
        "sky130_fd_sc_lp__and2_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2_4": _logic_module(
        "sky130_fd_sc_lp__and2_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2_lp2": _logic_module(
        "sky130_fd_sc_lp__and2_lp2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2_lp": _logic_module(
        "sky130_fd_sc_lp__and2_lp",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2_m": _logic_module(
        "sky130_fd_sc_lp__and2_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2b_1": _logic_module(
        "sky130_fd_sc_lp__and2b_1",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2b_2": _logic_module(
        "sky130_fd_sc_lp__and2b_2",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2b_4": _logic_module(
        "sky130_fd_sc_lp__and2b_4",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2b_lp": _logic_module(
        "sky130_fd_sc_lp__and2b_lp",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and2b_m": _logic_module(
        "sky130_fd_sc_lp__and2b_m",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3_0": _logic_module(
        "sky130_fd_sc_lp__and3_0",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3_1": _logic_module(
        "sky130_fd_sc_lp__and3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3_2": _logic_module(
        "sky130_fd_sc_lp__and3_2",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3_4": _logic_module(
        "sky130_fd_sc_lp__and3_4",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3_lp": _logic_module(
        "sky130_fd_sc_lp__and3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3_m": _logic_module(
        "sky130_fd_sc_lp__and3_m",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3b_1": _logic_module(
        "sky130_fd_sc_lp__and3b_1",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3b_2": _logic_module(
        "sky130_fd_sc_lp__and3b_2",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3b_4": _logic_module(
        "sky130_fd_sc_lp__and3b_4",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3b_lp": _logic_module(
        "sky130_fd_sc_lp__and3b_lp",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and3b_m": _logic_module(
        "sky130_fd_sc_lp__and3b_m",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_0": _logic_module(
        "sky130_fd_sc_lp__and4_0",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_1": _logic_module(
        "sky130_fd_sc_lp__and4_1",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_2": _logic_module(
        "sky130_fd_sc_lp__and4_2",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_4": _logic_module(
        "sky130_fd_sc_lp__and4_4",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_lp2": _logic_module(
        "sky130_fd_sc_lp__and4_lp2",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_lp": _logic_module(
        "sky130_fd_sc_lp__and4_lp",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4_m": _logic_module(
        "sky130_fd_sc_lp__and4_m",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4b_1": _logic_module(
        "sky130_fd_sc_lp__and4b_1",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4b_2": _logic_module(
        "sky130_fd_sc_lp__and4b_2",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4b_4": _logic_module(
        "sky130_fd_sc_lp__and4b_4",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4b_lp": _logic_module(
        "sky130_fd_sc_lp__and4b_lp",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4b_m": _logic_module(
        "sky130_fd_sc_lp__and4b_m",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4bb_1": _logic_module(
        "sky130_fd_sc_lp__and4bb_1",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4bb_2": _logic_module(
        "sky130_fd_sc_lp__and4bb_2",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4bb_4": _logic_module(
        "sky130_fd_sc_lp__and4bb_4",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4bb_lp": _logic_module(
        "sky130_fd_sc_lp__and4bb_lp",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__and4bb_m": _logic_module(
        "sky130_fd_sc_lp__and4bb_m",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buf_0": _logic_module(
        "sky130_fd_sc_lp__buf_0", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_1": _logic_module(
        "sky130_fd_sc_lp__buf_1", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_2": _logic_module(
        "sky130_fd_sc_lp__buf_2", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_4": _logic_module(
        "sky130_fd_sc_lp__buf_4", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_8": _logic_module(
        "sky130_fd_sc_lp__buf_8", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_16": _logic_module(
        "sky130_fd_sc_lp__buf_16", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_lp": _logic_module(
        "sky130_fd_sc_lp__buf_lp", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__buf_m": _logic_module(
        "sky130_fd_sc_lp__buf_m", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_lp__bufbuf_8": _logic_module(
        "sky130_fd_sc_lp__bufbuf_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__bufbuf_16": _logic_module(
        "sky130_fd_sc_lp__bufbuf_16",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__bufinv_8": _logic_module(
        "sky130_fd_sc_lp__bufinv_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__bufinv_16": _logic_module(
        "sky130_fd_sc_lp__bufinv_16",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__bufkapwr_1": _logic_module(
        "sky130_fd_sc_lp__bufkapwr_1",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__bufkapwr_2": _logic_module(
        "sky130_fd_sc_lp__bufkapwr_2",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__bufkapwr_4": _logic_module(
        "sky130_fd_sc_lp__bufkapwr_4",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__bufkapwr_8": _logic_module(
        "sky130_fd_sc_lp__bufkapwr_8",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buflp_0": _logic_module(
        "sky130_fd_sc_lp__buflp_0",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buflp_1": _logic_module(
        "sky130_fd_sc_lp__buflp_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buflp_2": _logic_module(
        "sky130_fd_sc_lp__buflp_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buflp_4": _logic_module(
        "sky130_fd_sc_lp__buflp_4",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buflp_8": _logic_module(
        "sky130_fd_sc_lp__buflp_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__buflp_m": _logic_module(
        "sky130_fd_sc_lp__buflp_m",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__busdriver2_20": _logic_module(
        "sky130_fd_sc_lp__busdriver2_20",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__busdriver_20": _logic_module(
        "sky130_fd_sc_lp__busdriver_20",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__busdrivernovlp2_20": _logic_module(
        "sky130_fd_sc_lp__busdrivernovlp2_20",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__busdrivernovlp_20": _logic_module(
        "sky130_fd_sc_lp__busdrivernovlp_20",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__busdrivernovlpsleep_20": _logic_module(
        "sky130_fd_sc_lp__busdrivernovlpsleep_20",
        "Low Power",
        ["A", "SLEEP", "TE_B", "KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__bushold0_1": _logic_module(
        "sky130_fd_sc_lp__bushold0_1",
        "Low Power",
        ["RESET", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__bushold_1": _logic_module(
        "sky130_fd_sc_lp__bushold_1",
        "Low Power",
        ["RESET", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__busreceiver_0": _logic_module(
        "sky130_fd_sc_lp__busreceiver_0",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__busreceiver_1": _logic_module(
        "sky130_fd_sc_lp__busreceiver_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__busreceiver_m": _logic_module(
        "sky130_fd_sc_lp__busreceiver_m",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_0": _logic_module(
        "sky130_fd_sc_lp__clkbuf_0",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_1": _logic_module(
        "sky130_fd_sc_lp__clkbuf_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_2": _logic_module(
        "sky130_fd_sc_lp__clkbuf_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_4": _logic_module(
        "sky130_fd_sc_lp__clkbuf_4",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_8": _logic_module(
        "sky130_fd_sc_lp__clkbuf_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_16": _logic_module(
        "sky130_fd_sc_lp__clkbuf_16",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuf_lp": _logic_module(
        "sky130_fd_sc_lp__clkbuf_lp",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuflp_2": _logic_module(
        "sky130_fd_sc_lp__clkbuflp_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuflp_4": _logic_module(
        "sky130_fd_sc_lp__clkbuflp_4",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuflp_8": _logic_module(
        "sky130_fd_sc_lp__clkbuflp_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkbuflp_16": _logic_module(
        "sky130_fd_sc_lp__clkbuflp_16",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s15_1": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s15_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s15_2": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s15_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s18_1": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s18_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s18_2": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s18_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s25_1": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s25_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s25_2": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s25_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s50_1": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s50_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkdlybuf4s50_2": _logic_module(
        "sky130_fd_sc_lp__clkdlybuf4s50_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__clkinv_0": _logic_module(
        "sky130_fd_sc_lp__clkinv_0",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_1": _logic_module(
        "sky130_fd_sc_lp__clkinv_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_2": _logic_module(
        "sky130_fd_sc_lp__clkinv_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_4": _logic_module(
        "sky130_fd_sc_lp__clkinv_4",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_8": _logic_module(
        "sky130_fd_sc_lp__clkinv_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_16": _logic_module(
        "sky130_fd_sc_lp__clkinv_16",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_lp2": _logic_module(
        "sky130_fd_sc_lp__clkinv_lp2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinv_lp": _logic_module(
        "sky130_fd_sc_lp__clkinv_lp",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinvlp_2": _logic_module(
        "sky130_fd_sc_lp__clkinvlp_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinvlp_4": _logic_module(
        "sky130_fd_sc_lp__clkinvlp_4",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinvlp_8": _logic_module(
        "sky130_fd_sc_lp__clkinvlp_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__clkinvlp_16": _logic_module(
        "sky130_fd_sc_lp__clkinvlp_16",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__conb_0": _logic_module(
        "sky130_fd_sc_lp__conb_0",
        "Low Power",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_lp__conb_1": _logic_module(
        "sky130_fd_sc_lp__conb_1",
        "Low Power",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_lp__decap_3": _logic_module(
        "sky130_fd_sc_lp__decap_3", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__decap_4": _logic_module(
        "sky130_fd_sc_lp__decap_4", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__decap_6": _logic_module(
        "sky130_fd_sc_lp__decap_6", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__decap_8": _logic_module(
        "sky130_fd_sc_lp__decap_8", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__decap_12": _logic_module(
        "sky130_fd_sc_lp__decap_12", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__decapkapwr_3": _logic_module(
        "sky130_fd_sc_lp__decapkapwr_3",
        "Low Power",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__decapkapwr_4": _logic_module(
        "sky130_fd_sc_lp__decapkapwr_4",
        "Low Power",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__decapkapwr_6": _logic_module(
        "sky130_fd_sc_lp__decapkapwr_6",
        "Low Power",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__decapkapwr_8": _logic_module(
        "sky130_fd_sc_lp__decapkapwr_8",
        "Low Power",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__decapkapwr_12": _logic_module(
        "sky130_fd_sc_lp__decapkapwr_12",
        "Low Power",
        ["KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__dfbbn_1": _logic_module(
        "sky130_fd_sc_lp__dfbbn_1",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfbbn_2": _logic_module(
        "sky130_fd_sc_lp__dfbbn_2",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfbbp_1": _logic_module(
        "sky130_fd_sc_lp__dfbbp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfrbp_1": _logic_module(
        "sky130_fd_sc_lp__dfrbp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfrbp_2": _logic_module(
        "sky130_fd_sc_lp__dfrbp_2",
        "Low Power",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfrbp_lp": _logic_module(
        "sky130_fd_sc_lp__dfrbp_lp",
        "Low Power",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfrtn_1": _logic_module(
        "sky130_fd_sc_lp__dfrtn_1",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfrtp_1": _logic_module(
        "sky130_fd_sc_lp__dfrtp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfrtp_2": _logic_module(
        "sky130_fd_sc_lp__dfrtp_2",
        "Low Power",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfrtp_4": _logic_module(
        "sky130_fd_sc_lp__dfrtp_4",
        "Low Power",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfsbp_1": _logic_module(
        "sky130_fd_sc_lp__dfsbp_1",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfsbp_2": _logic_module(
        "sky130_fd_sc_lp__dfsbp_2",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfsbp_lp": _logic_module(
        "sky130_fd_sc_lp__dfsbp_lp",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfstp_1": _logic_module(
        "sky130_fd_sc_lp__dfstp_1",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfstp_2": _logic_module(
        "sky130_fd_sc_lp__dfstp_2",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfstp_4": _logic_module(
        "sky130_fd_sc_lp__dfstp_4",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfstp_lp": _logic_module(
        "sky130_fd_sc_lp__dfstp_lp",
        "Low Power",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfxbp_1": _logic_module(
        "sky130_fd_sc_lp__dfxbp_1",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfxbp_2": _logic_module(
        "sky130_fd_sc_lp__dfxbp_2",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfxbp_lp": _logic_module(
        "sky130_fd_sc_lp__dfxbp_lp",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dfxtp_1": _logic_module(
        "sky130_fd_sc_lp__dfxtp_1",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfxtp_2": _logic_module(
        "sky130_fd_sc_lp__dfxtp_2",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfxtp_4": _logic_module(
        "sky130_fd_sc_lp__dfxtp_4",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dfxtp_lp": _logic_module(
        "sky130_fd_sc_lp__dfxtp_lp",
        "Low Power",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__diode_0": _logic_module(
        "sky130_fd_sc_lp__diode_0", "Low Power", ["DIODE", "VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__diode_1": _logic_module(
        "sky130_fd_sc_lp__diode_1", "Low Power", ["DIODE", "VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__dlclkp_1": _logic_module(
        "sky130_fd_sc_lp__dlclkp_1",
        "Low Power",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__dlclkp_2": _logic_module(
        "sky130_fd_sc_lp__dlclkp_2",
        "Low Power",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__dlclkp_4": _logic_module(
        "sky130_fd_sc_lp__dlclkp_4",
        "Low Power",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__dlclkp_lp": _logic_module(
        "sky130_fd_sc_lp__dlclkp_lp",
        "Low Power",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__dlrbn_1": _logic_module(
        "sky130_fd_sc_lp__dlrbn_1",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlrbn_2": _logic_module(
        "sky130_fd_sc_lp__dlrbn_2",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlrbn_lp": _logic_module(
        "sky130_fd_sc_lp__dlrbn_lp",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlrbp_1": _logic_module(
        "sky130_fd_sc_lp__dlrbp_1",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlrbp_2": _logic_module(
        "sky130_fd_sc_lp__dlrbp_2",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlrbp_lp": _logic_module(
        "sky130_fd_sc_lp__dlrbp_lp",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlrtn_1": _logic_module(
        "sky130_fd_sc_lp__dlrtn_1",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtn_2": _logic_module(
        "sky130_fd_sc_lp__dlrtn_2",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtn_4": _logic_module(
        "sky130_fd_sc_lp__dlrtn_4",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtn_lp": _logic_module(
        "sky130_fd_sc_lp__dlrtn_lp",
        "Low Power",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtp_1": _logic_module(
        "sky130_fd_sc_lp__dlrtp_1",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtp_2": _logic_module(
        "sky130_fd_sc_lp__dlrtp_2",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtp_4": _logic_module(
        "sky130_fd_sc_lp__dlrtp_4",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtp_lp2": _logic_module(
        "sky130_fd_sc_lp__dlrtp_lp2",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlrtp_lp": _logic_module(
        "sky130_fd_sc_lp__dlrtp_lp",
        "Low Power",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlxbn_1": _logic_module(
        "sky130_fd_sc_lp__dlxbn_1",
        "Low Power",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlxbn_2": _logic_module(
        "sky130_fd_sc_lp__dlxbn_2",
        "Low Power",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlxbp_1": _logic_module(
        "sky130_fd_sc_lp__dlxbp_1",
        "Low Power",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlxbp_lp2": _logic_module(
        "sky130_fd_sc_lp__dlxbp_lp2",
        "Low Power",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlxbp_lp": _logic_module(
        "sky130_fd_sc_lp__dlxbp_lp",
        "Low Power",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__dlxtn_1": _logic_module(
        "sky130_fd_sc_lp__dlxtn_1",
        "Low Power",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlxtn_2": _logic_module(
        "sky130_fd_sc_lp__dlxtn_2",
        "Low Power",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlxtn_4": _logic_module(
        "sky130_fd_sc_lp__dlxtn_4",
        "Low Power",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlxtp_1": _logic_module(
        "sky130_fd_sc_lp__dlxtp_1",
        "Low Power",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlxtp_lp2": _logic_module(
        "sky130_fd_sc_lp__dlxtp_lp2",
        "Low Power",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlxtp_lp": _logic_module(
        "sky130_fd_sc_lp__dlxtp_lp",
        "Low Power",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__dlybuf4s15kapwr_1": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s15kapwr_1",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s15kapwr_2": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s15kapwr_2",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s18kapwr_1": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s18kapwr_1",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s18kapwr_2": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s18kapwr_2",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s25kapwr_1": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s25kapwr_1",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s25kapwr_2": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s25kapwr_2",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s50kapwr_1": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s50kapwr_1",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlybuf4s50kapwr_2": _logic_module(
        "sky130_fd_sc_lp__dlybuf4s50kapwr_2",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlygate4s15_1": _logic_module(
        "sky130_fd_sc_lp__dlygate4s15_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlygate4s18_1": _logic_module(
        "sky130_fd_sc_lp__dlygate4s18_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlygate4s50_1": _logic_module(
        "sky130_fd_sc_lp__dlygate4s50_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlymetal6s2s_1": _logic_module(
        "sky130_fd_sc_lp__dlymetal6s2s_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlymetal6s4s_1": _logic_module(
        "sky130_fd_sc_lp__dlymetal6s4s_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__dlymetal6s6s_1": _logic_module(
        "sky130_fd_sc_lp__dlymetal6s6s_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__ebufn_1": _logic_module(
        "sky130_fd_sc_lp__ebufn_1",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__ebufn_2": _logic_module(
        "sky130_fd_sc_lp__ebufn_2",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__ebufn_4": _logic_module(
        "sky130_fd_sc_lp__ebufn_4",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__ebufn_8": _logic_module(
        "sky130_fd_sc_lp__ebufn_8",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__ebufn_lp2": _logic_module(
        "sky130_fd_sc_lp__ebufn_lp2",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__ebufn_lp": _logic_module(
        "sky130_fd_sc_lp__ebufn_lp",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__edfxbp_1": _logic_module(
        "sky130_fd_sc_lp__edfxbp_1",
        "Low Power",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__einvn_0": _logic_module(
        "sky130_fd_sc_lp__einvn_0",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvn_1": _logic_module(
        "sky130_fd_sc_lp__einvn_1",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvn_2": _logic_module(
        "sky130_fd_sc_lp__einvn_2",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvn_4": _logic_module(
        "sky130_fd_sc_lp__einvn_4",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvn_8": _logic_module(
        "sky130_fd_sc_lp__einvn_8",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvn_lp": _logic_module(
        "sky130_fd_sc_lp__einvn_lp",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvn_m": _logic_module(
        "sky130_fd_sc_lp__einvn_m",
        "Low Power",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_0": _logic_module(
        "sky130_fd_sc_lp__einvp_0",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_1": _logic_module(
        "sky130_fd_sc_lp__einvp_1",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_2": _logic_module(
        "sky130_fd_sc_lp__einvp_2",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_4": _logic_module(
        "sky130_fd_sc_lp__einvp_4",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_8": _logic_module(
        "sky130_fd_sc_lp__einvp_8",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_lp": _logic_module(
        "sky130_fd_sc_lp__einvp_lp",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__einvp_m": _logic_module(
        "sky130_fd_sc_lp__einvp_m",
        "Low Power",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_lp__fa_0": _logic_module(
        "sky130_fd_sc_lp__fa_0",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fa_1": _logic_module(
        "sky130_fd_sc_lp__fa_1",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fa_2": _logic_module(
        "sky130_fd_sc_lp__fa_2",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fa_4": _logic_module(
        "sky130_fd_sc_lp__fa_4",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fa_lp": _logic_module(
        "sky130_fd_sc_lp__fa_lp",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fa_m": _logic_module(
        "sky130_fd_sc_lp__fa_m",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fah_1": _logic_module(
        "sky130_fd_sc_lp__fah_1",
        "Low Power",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fahcin_1": _logic_module(
        "sky130_fd_sc_lp__fahcin_1",
        "Low Power",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__fahcon_1": _logic_module(
        "sky130_fd_sc_lp__fahcon_1",
        "Low Power",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT_N", "SUM"],
    ),
    "sky130_fd_sc_lp__fill_1": _logic_module(
        "sky130_fd_sc_lp__fill_1", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__fill_2": _logic_module(
        "sky130_fd_sc_lp__fill_2", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__fill_4": _logic_module(
        "sky130_fd_sc_lp__fill_4", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__fill_8": _logic_module(
        "sky130_fd_sc_lp__fill_8", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__ha_0": _logic_module(
        "sky130_fd_sc_lp__ha_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__ha_1": _logic_module(
        "sky130_fd_sc_lp__ha_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__ha_2": _logic_module(
        "sky130_fd_sc_lp__ha_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__ha_4": _logic_module(
        "sky130_fd_sc_lp__ha_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__ha_lp": _logic_module(
        "sky130_fd_sc_lp__ha_lp",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__ha_m": _logic_module(
        "sky130_fd_sc_lp__ha_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_lp__inputiso0n_lp": _logic_module(
        "sky130_fd_sc_lp__inputiso0n_lp",
        "Low Power",
        ["A", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__inputiso0p_lp": _logic_module(
        "sky130_fd_sc_lp__inputiso0p_lp",
        "Low Power",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__inputiso1n_lp": _logic_module(
        "sky130_fd_sc_lp__inputiso1n_lp",
        "Low Power",
        ["A", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__inputiso1p_lp": _logic_module(
        "sky130_fd_sc_lp__inputiso1p_lp",
        "Low Power",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__inputisolatch_lp": _logic_module(
        "sky130_fd_sc_lp__inputisolatch_lp",
        "Low Power",
        ["D", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__inv_0": _logic_module(
        "sky130_fd_sc_lp__inv_0", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__inv_1": _logic_module(
        "sky130_fd_sc_lp__inv_1", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__inv_2": _logic_module(
        "sky130_fd_sc_lp__inv_2", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__inv_4": _logic_module(
        "sky130_fd_sc_lp__inv_4", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__inv_8": _logic_module(
        "sky130_fd_sc_lp__inv_8", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__inv_16": _logic_module(
        "sky130_fd_sc_lp__inv_16", "Low Power", ["A", "VGND", "VNB", "VPB", "Y"]
    ),
    "sky130_fd_sc_lp__inv_lp": _logic_module(
        "sky130_fd_sc_lp__inv_lp", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__inv_m": _logic_module(
        "sky130_fd_sc_lp__inv_m", "Low Power", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_lp__invkapwr_1": _logic_module(
        "sky130_fd_sc_lp__invkapwr_1",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invkapwr_2": _logic_module(
        "sky130_fd_sc_lp__invkapwr_2",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invkapwr_4": _logic_module(
        "sky130_fd_sc_lp__invkapwr_4",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invkapwr_8": _logic_module(
        "sky130_fd_sc_lp__invkapwr_8",
        "Low Power",
        ["A", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invlp_0": _logic_module(
        "sky130_fd_sc_lp__invlp_0",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invlp_1": _logic_module(
        "sky130_fd_sc_lp__invlp_1",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invlp_2": _logic_module(
        "sky130_fd_sc_lp__invlp_2",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invlp_4": _logic_module(
        "sky130_fd_sc_lp__invlp_4",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invlp_8": _logic_module(
        "sky130_fd_sc_lp__invlp_8",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__invlp_m": _logic_module(
        "sky130_fd_sc_lp__invlp_m",
        "Low Power",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__iso0n_lp2": _logic_module(
        "sky130_fd_sc_lp__iso0n_lp2",
        "Low Power",
        ["A", "SLEEP_B", "KAGND", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso0n_lp": _logic_module(
        "sky130_fd_sc_lp__iso0n_lp",
        "Low Power",
        ["A", "KAGND", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso0p_lp2": _logic_module(
        "sky130_fd_sc_lp__iso0p_lp2",
        "Low Power",
        ["A", "SLEEP", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso0p_lp": _logic_module(
        "sky130_fd_sc_lp__iso0p_lp",
        "Low Power",
        ["A", "KAPWR", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso1n_lp2": _logic_module(
        "sky130_fd_sc_lp__iso1n_lp2",
        "Low Power",
        ["A", "SLEEP_B", "KAGND", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso1n_lp": _logic_module(
        "sky130_fd_sc_lp__iso1n_lp",
        "Low Power",
        ["A", "KAGND", "SLEEP_B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso1p_lp2": _logic_module(
        "sky130_fd_sc_lp__iso1p_lp2",
        "Low Power",
        ["A", "SLEEP", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__iso1p_lp": _logic_module(
        "sky130_fd_sc_lp__iso1p_lp",
        "Low Power",
        ["A", "KAPWR", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__isobufsrc_1": _logic_module(
        "sky130_fd_sc_lp__isobufsrc_1",
        "Low Power",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__isobufsrc_2": _logic_module(
        "sky130_fd_sc_lp__isobufsrc_2",
        "Low Power",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__isobufsrc_4": _logic_module(
        "sky130_fd_sc_lp__isobufsrc_4",
        "Low Power",
        ["A", "SLEEP", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__isolatch_lp": _logic_module(
        "sky130_fd_sc_lp__isolatch_lp",
        "Low Power",
        ["D", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__lsbuf_lp": _logic_module(
        "sky130_fd_sc_lp__lsbuf_lp",
        "Low Power",
        ["A", "DESTPWR", "DESTVPB", "VGND", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__lsbufiso0p_lp": _logic_module(
        "sky130_fd_sc_lp__lsbufiso0p_lp",
        "Low Power",
        ["A", "DESTPWR", "DESTVPB", "SLEEP", "VGND", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__lsbufiso1p_lp": _logic_module(
        "sky130_fd_sc_lp__lsbufiso1p_lp",
        "Low Power",
        ["A", "DESTPWR", "DESTVPB", "SLEEP", "VGND", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__maj3_0": _logic_module(
        "sky130_fd_sc_lp__maj3_0",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__maj3_1": _logic_module(
        "sky130_fd_sc_lp__maj3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__maj3_2": _logic_module(
        "sky130_fd_sc_lp__maj3_2",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__maj3_4": _logic_module(
        "sky130_fd_sc_lp__maj3_4",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__maj3_lp": _logic_module(
        "sky130_fd_sc_lp__maj3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__maj3_m": _logic_module(
        "sky130_fd_sc_lp__maj3_m",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_0": _logic_module(
        "sky130_fd_sc_lp__mux2_0",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_1": _logic_module(
        "sky130_fd_sc_lp__mux2_1",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_2": _logic_module(
        "sky130_fd_sc_lp__mux2_2",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_4": _logic_module(
        "sky130_fd_sc_lp__mux2_4",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_8": _logic_module(
        "sky130_fd_sc_lp__mux2_8",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_lp2": _logic_module(
        "sky130_fd_sc_lp__mux2_lp2",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_lp": _logic_module(
        "sky130_fd_sc_lp__mux2_lp",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2_m": _logic_module(
        "sky130_fd_sc_lp__mux2_m",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux2i_0": _logic_module(
        "sky130_fd_sc_lp__mux2i_0",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux2i_1": _logic_module(
        "sky130_fd_sc_lp__mux2i_1",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux2i_2": _logic_module(
        "sky130_fd_sc_lp__mux2i_2",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux2i_4": _logic_module(
        "sky130_fd_sc_lp__mux2i_4",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux2i_lp2": _logic_module(
        "sky130_fd_sc_lp__mux2i_lp2",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux2i_lp": _logic_module(
        "sky130_fd_sc_lp__mux2i_lp",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux2i_m": _logic_module(
        "sky130_fd_sc_lp__mux2i_m",
        "Low Power",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__mux4_0": _logic_module(
        "sky130_fd_sc_lp__mux4_0",
        "Low Power",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux4_1": _logic_module(
        "sky130_fd_sc_lp__mux4_1",
        "Low Power",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux4_2": _logic_module(
        "sky130_fd_sc_lp__mux4_2",
        "Low Power",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux4_4": _logic_module(
        "sky130_fd_sc_lp__mux4_4",
        "Low Power",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux4_lp": _logic_module(
        "sky130_fd_sc_lp__mux4_lp",
        "Low Power",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__mux4_m": _logic_module(
        "sky130_fd_sc_lp__mux4_m",
        "Low Power",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__nand2_0": _logic_module(
        "sky130_fd_sc_lp__nand2_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_1": _logic_module(
        "sky130_fd_sc_lp__nand2_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_2": _logic_module(
        "sky130_fd_sc_lp__nand2_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_4": _logic_module(
        "sky130_fd_sc_lp__nand2_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_8": _logic_module(
        "sky130_fd_sc_lp__nand2_8",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_lp2": _logic_module(
        "sky130_fd_sc_lp__nand2_lp2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_lp": _logic_module(
        "sky130_fd_sc_lp__nand2_lp",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2_m": _logic_module(
        "sky130_fd_sc_lp__nand2_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2b_1": _logic_module(
        "sky130_fd_sc_lp__nand2b_1",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2b_2": _logic_module(
        "sky130_fd_sc_lp__nand2b_2",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2b_4": _logic_module(
        "sky130_fd_sc_lp__nand2b_4",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2b_lp": _logic_module(
        "sky130_fd_sc_lp__nand2b_lp",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand2b_m": _logic_module(
        "sky130_fd_sc_lp__nand2b_m",
        "Low Power",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3_0": _logic_module(
        "sky130_fd_sc_lp__nand3_0",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3_1": _logic_module(
        "sky130_fd_sc_lp__nand3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3_2": _logic_module(
        "sky130_fd_sc_lp__nand3_2",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3_4": _logic_module(
        "sky130_fd_sc_lp__nand3_4",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3_lp": _logic_module(
        "sky130_fd_sc_lp__nand3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3_m": _logic_module(
        "sky130_fd_sc_lp__nand3_m",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3b_1": _logic_module(
        "sky130_fd_sc_lp__nand3b_1",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3b_2": _logic_module(
        "sky130_fd_sc_lp__nand3b_2",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3b_4": _logic_module(
        "sky130_fd_sc_lp__nand3b_4",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3b_lp": _logic_module(
        "sky130_fd_sc_lp__nand3b_lp",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand3b_m": _logic_module(
        "sky130_fd_sc_lp__nand3b_m",
        "Low Power",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4_0": _logic_module(
        "sky130_fd_sc_lp__nand4_0",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4_1": _logic_module(
        "sky130_fd_sc_lp__nand4_1",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4_2": _logic_module(
        "sky130_fd_sc_lp__nand4_2",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4_4": _logic_module(
        "sky130_fd_sc_lp__nand4_4",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4_lp": _logic_module(
        "sky130_fd_sc_lp__nand4_lp",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4_m": _logic_module(
        "sky130_fd_sc_lp__nand4_m",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4b_1": _logic_module(
        "sky130_fd_sc_lp__nand4b_1",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4b_2": _logic_module(
        "sky130_fd_sc_lp__nand4b_2",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4b_4": _logic_module(
        "sky130_fd_sc_lp__nand4b_4",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4b_lp": _logic_module(
        "sky130_fd_sc_lp__nand4b_lp",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4b_m": _logic_module(
        "sky130_fd_sc_lp__nand4b_m",
        "Low Power",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4bb_1": _logic_module(
        "sky130_fd_sc_lp__nand4bb_1",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4bb_2": _logic_module(
        "sky130_fd_sc_lp__nand4bb_2",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4bb_4": _logic_module(
        "sky130_fd_sc_lp__nand4bb_4",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4bb_lp": _logic_module(
        "sky130_fd_sc_lp__nand4bb_lp",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nand4bb_m": _logic_module(
        "sky130_fd_sc_lp__nand4bb_m",
        "Low Power",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_0": _logic_module(
        "sky130_fd_sc_lp__nor2_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_1": _logic_module(
        "sky130_fd_sc_lp__nor2_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_2": _logic_module(
        "sky130_fd_sc_lp__nor2_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_4": _logic_module(
        "sky130_fd_sc_lp__nor2_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_8": _logic_module(
        "sky130_fd_sc_lp__nor2_8",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_lp2": _logic_module(
        "sky130_fd_sc_lp__nor2_lp2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2_lp": _logic_module(
        "sky130_fd_sc_lp__nor2_lp", "Low Power", ["A", "B", "VNB", "VPB", "Y"]
    ),
    "sky130_fd_sc_lp__nor2_m": _logic_module(
        "sky130_fd_sc_lp__nor2_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2b_1": _logic_module(
        "sky130_fd_sc_lp__nor2b_1",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2b_2": _logic_module(
        "sky130_fd_sc_lp__nor2b_2",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2b_4": _logic_module(
        "sky130_fd_sc_lp__nor2b_4",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2b_lp": _logic_module(
        "sky130_fd_sc_lp__nor2b_lp",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor2b_m": _logic_module(
        "sky130_fd_sc_lp__nor2b_m",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3_0": _logic_module(
        "sky130_fd_sc_lp__nor3_0",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3_1": _logic_module(
        "sky130_fd_sc_lp__nor3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3_2": _logic_module(
        "sky130_fd_sc_lp__nor3_2",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3_4": _logic_module(
        "sky130_fd_sc_lp__nor3_4",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3_lp": _logic_module(
        "sky130_fd_sc_lp__nor3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3_m": _logic_module(
        "sky130_fd_sc_lp__nor3_m",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3b_1": _logic_module(
        "sky130_fd_sc_lp__nor3b_1",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3b_2": _logic_module(
        "sky130_fd_sc_lp__nor3b_2",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3b_4": _logic_module(
        "sky130_fd_sc_lp__nor3b_4",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3b_lp": _logic_module(
        "sky130_fd_sc_lp__nor3b_lp",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor3b_m": _logic_module(
        "sky130_fd_sc_lp__nor3b_m",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4_0": _logic_module(
        "sky130_fd_sc_lp__nor4_0",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4_1": _logic_module(
        "sky130_fd_sc_lp__nor4_1",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4_2": _logic_module(
        "sky130_fd_sc_lp__nor4_2",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4_4": _logic_module(
        "sky130_fd_sc_lp__nor4_4",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4_lp": _logic_module(
        "sky130_fd_sc_lp__nor4_lp",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4_m": _logic_module(
        "sky130_fd_sc_lp__nor4_m",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4b_1": _logic_module(
        "sky130_fd_sc_lp__nor4b_1",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4b_2": _logic_module(
        "sky130_fd_sc_lp__nor4b_2",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4b_4": _logic_module(
        "sky130_fd_sc_lp__nor4b_4",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4b_lp": _logic_module(
        "sky130_fd_sc_lp__nor4b_lp",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4b_m": _logic_module(
        "sky130_fd_sc_lp__nor4b_m",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4bb_1": _logic_module(
        "sky130_fd_sc_lp__nor4bb_1",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4bb_2": _logic_module(
        "sky130_fd_sc_lp__nor4bb_2",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4bb_4": _logic_module(
        "sky130_fd_sc_lp__nor4bb_4",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4bb_lp": _logic_module(
        "sky130_fd_sc_lp__nor4bb_lp",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__nor4bb_m": _logic_module(
        "sky130_fd_sc_lp__nor4bb_m",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2bb2a_0": _logic_module(
        "sky130_fd_sc_lp__o2bb2a_0",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2bb2a_1": _logic_module(
        "sky130_fd_sc_lp__o2bb2a_1",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2bb2a_2": _logic_module(
        "sky130_fd_sc_lp__o2bb2a_2",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2bb2a_4": _logic_module(
        "sky130_fd_sc_lp__o2bb2a_4",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2bb2a_lp": _logic_module(
        "sky130_fd_sc_lp__o2bb2a_lp",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2bb2a_m": _logic_module(
        "sky130_fd_sc_lp__o2bb2a_m",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2bb2ai_0": _logic_module(
        "sky130_fd_sc_lp__o2bb2ai_0",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2bb2ai_1": _logic_module(
        "sky130_fd_sc_lp__o2bb2ai_1",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2bb2ai_2": _logic_module(
        "sky130_fd_sc_lp__o2bb2ai_2",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2bb2ai_4": _logic_module(
        "sky130_fd_sc_lp__o2bb2ai_4",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2bb2ai_lp": _logic_module(
        "sky130_fd_sc_lp__o2bb2ai_lp",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2bb2ai_m": _logic_module(
        "sky130_fd_sc_lp__o2bb2ai_m",
        "Low Power",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21a_0": _logic_module(
        "sky130_fd_sc_lp__o21a_0",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21a_1": _logic_module(
        "sky130_fd_sc_lp__o21a_1",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21a_2": _logic_module(
        "sky130_fd_sc_lp__o21a_2",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21a_4": _logic_module(
        "sky130_fd_sc_lp__o21a_4",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21a_lp": _logic_module(
        "sky130_fd_sc_lp__o21a_lp",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21a_m": _logic_module(
        "sky130_fd_sc_lp__o21a_m",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21ai_0": _logic_module(
        "sky130_fd_sc_lp__o21ai_0",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21ai_1": _logic_module(
        "sky130_fd_sc_lp__o21ai_1",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21ai_2": _logic_module(
        "sky130_fd_sc_lp__o21ai_2",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21ai_4": _logic_module(
        "sky130_fd_sc_lp__o21ai_4",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21ai_lp": _logic_module(
        "sky130_fd_sc_lp__o21ai_lp",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21ai_m": _logic_module(
        "sky130_fd_sc_lp__o21ai_m",
        "Low Power",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21ba_0": _logic_module(
        "sky130_fd_sc_lp__o21ba_0",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21ba_1": _logic_module(
        "sky130_fd_sc_lp__o21ba_1",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21ba_2": _logic_module(
        "sky130_fd_sc_lp__o21ba_2",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21ba_4": _logic_module(
        "sky130_fd_sc_lp__o21ba_4",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21ba_lp": _logic_module(
        "sky130_fd_sc_lp__o21ba_lp",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21ba_m": _logic_module(
        "sky130_fd_sc_lp__o21ba_m",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o21bai_0": _logic_module(
        "sky130_fd_sc_lp__o21bai_0",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21bai_1": _logic_module(
        "sky130_fd_sc_lp__o21bai_1",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21bai_2": _logic_module(
        "sky130_fd_sc_lp__o21bai_2",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21bai_4": _logic_module(
        "sky130_fd_sc_lp__o21bai_4",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21bai_lp": _logic_module(
        "sky130_fd_sc_lp__o21bai_lp",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o21bai_m": _logic_module(
        "sky130_fd_sc_lp__o21bai_m",
        "Low Power",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o22a_0": _logic_module(
        "sky130_fd_sc_lp__o22a_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o22a_1": _logic_module(
        "sky130_fd_sc_lp__o22a_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o22a_2": _logic_module(
        "sky130_fd_sc_lp__o22a_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o22a_4": _logic_module(
        "sky130_fd_sc_lp__o22a_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o22a_lp": _logic_module(
        "sky130_fd_sc_lp__o22a_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o22a_m": _logic_module(
        "sky130_fd_sc_lp__o22a_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o22ai_0": _logic_module(
        "sky130_fd_sc_lp__o22ai_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o22ai_1": _logic_module(
        "sky130_fd_sc_lp__o22ai_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o22ai_2": _logic_module(
        "sky130_fd_sc_lp__o22ai_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o22ai_4": _logic_module(
        "sky130_fd_sc_lp__o22ai_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o22ai_lp": _logic_module(
        "sky130_fd_sc_lp__o22ai_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o22ai_m": _logic_module(
        "sky130_fd_sc_lp__o22ai_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o31a_0": _logic_module(
        "sky130_fd_sc_lp__o31a_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o31a_1": _logic_module(
        "sky130_fd_sc_lp__o31a_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o31a_2": _logic_module(
        "sky130_fd_sc_lp__o31a_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o31a_4": _logic_module(
        "sky130_fd_sc_lp__o31a_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o31a_lp": _logic_module(
        "sky130_fd_sc_lp__o31a_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o31a_m": _logic_module(
        "sky130_fd_sc_lp__o31a_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o31ai_0": _logic_module(
        "sky130_fd_sc_lp__o31ai_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o31ai_1": _logic_module(
        "sky130_fd_sc_lp__o31ai_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o31ai_2": _logic_module(
        "sky130_fd_sc_lp__o31ai_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o31ai_4": _logic_module(
        "sky130_fd_sc_lp__o31ai_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o31ai_lp": _logic_module(
        "sky130_fd_sc_lp__o31ai_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o31ai_m": _logic_module(
        "sky130_fd_sc_lp__o31ai_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o32a_0": _logic_module(
        "sky130_fd_sc_lp__o32a_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o32a_1": _logic_module(
        "sky130_fd_sc_lp__o32a_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o32a_2": _logic_module(
        "sky130_fd_sc_lp__o32a_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o32a_4": _logic_module(
        "sky130_fd_sc_lp__o32a_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o32a_lp": _logic_module(
        "sky130_fd_sc_lp__o32a_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o32a_m": _logic_module(
        "sky130_fd_sc_lp__o32a_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o32ai_0": _logic_module(
        "sky130_fd_sc_lp__o32ai_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o32ai_1": _logic_module(
        "sky130_fd_sc_lp__o32ai_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o32ai_2": _logic_module(
        "sky130_fd_sc_lp__o32ai_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o32ai_4": _logic_module(
        "sky130_fd_sc_lp__o32ai_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o32ai_lp": _logic_module(
        "sky130_fd_sc_lp__o32ai_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o32ai_m": _logic_module(
        "sky130_fd_sc_lp__o32ai_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o41a_0": _logic_module(
        "sky130_fd_sc_lp__o41a_0",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o41a_1": _logic_module(
        "sky130_fd_sc_lp__o41a_1",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o41a_2": _logic_module(
        "sky130_fd_sc_lp__o41a_2",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o41a_4": _logic_module(
        "sky130_fd_sc_lp__o41a_4",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o41a_lp": _logic_module(
        "sky130_fd_sc_lp__o41a_lp",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o41a_m": _logic_module(
        "sky130_fd_sc_lp__o41a_m",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o41ai_0": _logic_module(
        "sky130_fd_sc_lp__o41ai_0",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o41ai_1": _logic_module(
        "sky130_fd_sc_lp__o41ai_1",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o41ai_2": _logic_module(
        "sky130_fd_sc_lp__o41ai_2",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o41ai_4": _logic_module(
        "sky130_fd_sc_lp__o41ai_4",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o41ai_lp": _logic_module(
        "sky130_fd_sc_lp__o41ai_lp",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o41ai_m": _logic_module(
        "sky130_fd_sc_lp__o41ai_m",
        "Low Power",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o211a_0": _logic_module(
        "sky130_fd_sc_lp__o211a_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o211a_1": _logic_module(
        "sky130_fd_sc_lp__o211a_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o211a_2": _logic_module(
        "sky130_fd_sc_lp__o211a_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o211a_4": _logic_module(
        "sky130_fd_sc_lp__o211a_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o211a_lp": _logic_module(
        "sky130_fd_sc_lp__o211a_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o211a_m": _logic_module(
        "sky130_fd_sc_lp__o211a_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o211ai_0": _logic_module(
        "sky130_fd_sc_lp__o211ai_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o211ai_1": _logic_module(
        "sky130_fd_sc_lp__o211ai_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o211ai_2": _logic_module(
        "sky130_fd_sc_lp__o211ai_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o211ai_4": _logic_module(
        "sky130_fd_sc_lp__o211ai_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o211ai_lp": _logic_module(
        "sky130_fd_sc_lp__o211ai_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o211ai_m": _logic_module(
        "sky130_fd_sc_lp__o211ai_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o221a_0": _logic_module(
        "sky130_fd_sc_lp__o221a_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o221a_1": _logic_module(
        "sky130_fd_sc_lp__o221a_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o221a_2": _logic_module(
        "sky130_fd_sc_lp__o221a_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o221a_4": _logic_module(
        "sky130_fd_sc_lp__o221a_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o221a_lp": _logic_module(
        "sky130_fd_sc_lp__o221a_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o221a_m": _logic_module(
        "sky130_fd_sc_lp__o221a_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o221ai_0": _logic_module(
        "sky130_fd_sc_lp__o221ai_0",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o221ai_1": _logic_module(
        "sky130_fd_sc_lp__o221ai_1",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o221ai_2": _logic_module(
        "sky130_fd_sc_lp__o221ai_2",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o221ai_4": _logic_module(
        "sky130_fd_sc_lp__o221ai_4",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o221ai_lp": _logic_module(
        "sky130_fd_sc_lp__o221ai_lp",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o221ai_m": _logic_module(
        "sky130_fd_sc_lp__o221ai_m",
        "Low Power",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o311a_0": _logic_module(
        "sky130_fd_sc_lp__o311a_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o311a_1": _logic_module(
        "sky130_fd_sc_lp__o311a_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o311a_2": _logic_module(
        "sky130_fd_sc_lp__o311a_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o311a_4": _logic_module(
        "sky130_fd_sc_lp__o311a_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o311a_lp": _logic_module(
        "sky130_fd_sc_lp__o311a_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o311a_m": _logic_module(
        "sky130_fd_sc_lp__o311a_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o311ai_0": _logic_module(
        "sky130_fd_sc_lp__o311ai_0",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o311ai_1": _logic_module(
        "sky130_fd_sc_lp__o311ai_1",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o311ai_2": _logic_module(
        "sky130_fd_sc_lp__o311ai_2",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o311ai_4": _logic_module(
        "sky130_fd_sc_lp__o311ai_4",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o311ai_lp": _logic_module(
        "sky130_fd_sc_lp__o311ai_lp",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o311ai_m": _logic_module(
        "sky130_fd_sc_lp__o311ai_m",
        "Low Power",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2111a_0": _logic_module(
        "sky130_fd_sc_lp__o2111a_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2111a_1": _logic_module(
        "sky130_fd_sc_lp__o2111a_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2111a_2": _logic_module(
        "sky130_fd_sc_lp__o2111a_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2111a_4": _logic_module(
        "sky130_fd_sc_lp__o2111a_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2111a_lp": _logic_module(
        "sky130_fd_sc_lp__o2111a_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2111a_m": _logic_module(
        "sky130_fd_sc_lp__o2111a_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__o2111ai_0": _logic_module(
        "sky130_fd_sc_lp__o2111ai_0",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2111ai_1": _logic_module(
        "sky130_fd_sc_lp__o2111ai_1",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2111ai_2": _logic_module(
        "sky130_fd_sc_lp__o2111ai_2",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2111ai_4": _logic_module(
        "sky130_fd_sc_lp__o2111ai_4",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2111ai_lp": _logic_module(
        "sky130_fd_sc_lp__o2111ai_lp",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__o2111ai_m": _logic_module(
        "sky130_fd_sc_lp__o2111ai_m",
        "Low Power",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__or2_0": _logic_module(
        "sky130_fd_sc_lp__or2_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2_1": _logic_module(
        "sky130_fd_sc_lp__or2_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2_2": _logic_module(
        "sky130_fd_sc_lp__or2_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2_4": _logic_module(
        "sky130_fd_sc_lp__or2_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2_lp2": _logic_module(
        "sky130_fd_sc_lp__or2_lp2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2_lp": _logic_module(
        "sky130_fd_sc_lp__or2_lp",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2_m": _logic_module(
        "sky130_fd_sc_lp__or2_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2b_1": _logic_module(
        "sky130_fd_sc_lp__or2b_1",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2b_2": _logic_module(
        "sky130_fd_sc_lp__or2b_2",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2b_4": _logic_module(
        "sky130_fd_sc_lp__or2b_4",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2b_lp": _logic_module(
        "sky130_fd_sc_lp__or2b_lp",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or2b_m": _logic_module(
        "sky130_fd_sc_lp__or2b_m",
        "Low Power",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3_0": _logic_module(
        "sky130_fd_sc_lp__or3_0",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3_1": _logic_module(
        "sky130_fd_sc_lp__or3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3_2": _logic_module(
        "sky130_fd_sc_lp__or3_2",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3_4": _logic_module(
        "sky130_fd_sc_lp__or3_4",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3_lp": _logic_module(
        "sky130_fd_sc_lp__or3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3_m": _logic_module(
        "sky130_fd_sc_lp__or3_m",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3b_1": _logic_module(
        "sky130_fd_sc_lp__or3b_1",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3b_2": _logic_module(
        "sky130_fd_sc_lp__or3b_2",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3b_4": _logic_module(
        "sky130_fd_sc_lp__or3b_4",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3b_lp": _logic_module(
        "sky130_fd_sc_lp__or3b_lp",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or3b_m": _logic_module(
        "sky130_fd_sc_lp__or3b_m",
        "Low Power",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4_0": _logic_module(
        "sky130_fd_sc_lp__or4_0",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4_1": _logic_module(
        "sky130_fd_sc_lp__or4_1",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4_2": _logic_module(
        "sky130_fd_sc_lp__or4_2",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4_4": _logic_module(
        "sky130_fd_sc_lp__or4_4",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4_lp": _logic_module(
        "sky130_fd_sc_lp__or4_lp",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4_m": _logic_module(
        "sky130_fd_sc_lp__or4_m",
        "Low Power",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4b_1": _logic_module(
        "sky130_fd_sc_lp__or4b_1",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4b_2": _logic_module(
        "sky130_fd_sc_lp__or4b_2",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4b_4": _logic_module(
        "sky130_fd_sc_lp__or4b_4",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4b_lp": _logic_module(
        "sky130_fd_sc_lp__or4b_lp",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4b_m": _logic_module(
        "sky130_fd_sc_lp__or4b_m",
        "Low Power",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4bb_1": _logic_module(
        "sky130_fd_sc_lp__or4bb_1",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4bb_2": _logic_module(
        "sky130_fd_sc_lp__or4bb_2",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4bb_4": _logic_module(
        "sky130_fd_sc_lp__or4bb_4",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4bb_lp": _logic_module(
        "sky130_fd_sc_lp__or4bb_lp",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__or4bb_m": _logic_module(
        "sky130_fd_sc_lp__or4bb_m",
        "Low Power",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__sdfbbn_1": _logic_module(
        "sky130_fd_sc_lp__sdfbbn_1",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__sdfbbn_2": _logic_module(
        "sky130_fd_sc_lp__sdfbbn_2",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__sdfbbp_1": _logic_module(
        "sky130_fd_sc_lp__sdfbbp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "SET_B", "VNB", "VPB", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfrbp_1": _logic_module(
        "sky130_fd_sc_lp__sdfrbp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfrbp_2": _logic_module(
        "sky130_fd_sc_lp__sdfrbp_2",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfrbp_lp": _logic_module(
        "sky130_fd_sc_lp__sdfrbp_lp",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfrtn_1": _logic_module(
        "sky130_fd_sc_lp__sdfrtn_1",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfrtp_1": _logic_module(
        "sky130_fd_sc_lp__sdfrtp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfrtp_2": _logic_module(
        "sky130_fd_sc_lp__sdfrtp_2",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfrtp_4": _logic_module(
        "sky130_fd_sc_lp__sdfrtp_4",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfrtp_lp2": _logic_module(
        "sky130_fd_sc_lp__sdfrtp_lp2",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfrtp_ov2": _logic_module(
        "sky130_fd_sc_lp__sdfrtp_ov2",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfsbp_1": _logic_module(
        "sky130_fd_sc_lp__sdfsbp_1",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfsbp_2": _logic_module(
        "sky130_fd_sc_lp__sdfsbp_2",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfsbp_lp": _logic_module(
        "sky130_fd_sc_lp__sdfsbp_lp",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfstp_1": _logic_module(
        "sky130_fd_sc_lp__sdfstp_1",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfstp_2": _logic_module(
        "sky130_fd_sc_lp__sdfstp_2",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfstp_4": _logic_module(
        "sky130_fd_sc_lp__sdfstp_4",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfstp_lp": _logic_module(
        "sky130_fd_sc_lp__sdfstp_lp",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfxbp_1": _logic_module(
        "sky130_fd_sc_lp__sdfxbp_1",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfxbp_2": _logic_module(
        "sky130_fd_sc_lp__sdfxbp_2",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfxbp_lp": _logic_module(
        "sky130_fd_sc_lp__sdfxbp_lp",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sdfxtp_1": _logic_module(
        "sky130_fd_sc_lp__sdfxtp_1",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfxtp_2": _logic_module(
        "sky130_fd_sc_lp__sdfxtp_2",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfxtp_4": _logic_module(
        "sky130_fd_sc_lp__sdfxtp_4",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdfxtp_lp": _logic_module(
        "sky130_fd_sc_lp__sdfxtp_lp",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sdlclkp_1": _logic_module(
        "sky130_fd_sc_lp__sdlclkp_1",
        "Low Power",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__sdlclkp_2": _logic_module(
        "sky130_fd_sc_lp__sdlclkp_2",
        "Low Power",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__sdlclkp_4": _logic_module(
        "sky130_fd_sc_lp__sdlclkp_4",
        "Low Power",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__sdlclkp_lp": _logic_module(
        "sky130_fd_sc_lp__sdlclkp_lp",
        "Low Power",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_lp__sleep_pargate_plv_7": _logic_module(
        "sky130_fd_sc_lp__sleep_pargate_plv_7",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__sleep_pargate_plv_14": _logic_module(
        "sky130_fd_sc_lp__sleep_pargate_plv_14",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__sleep_pargate_plv_21": _logic_module(
        "sky130_fd_sc_lp__sleep_pargate_plv_21",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__sleep_pargate_plv_28": _logic_module(
        "sky130_fd_sc_lp__sleep_pargate_plv_28",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__sleep_sergate_plv_14": _logic_module(
        "sky130_fd_sc_lp__sleep_sergate_plv_14",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__sleep_sergate_plv_21": _logic_module(
        "sky130_fd_sc_lp__sleep_sergate_plv_21",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__sleep_sergate_plv_28": _logic_module(
        "sky130_fd_sc_lp__sleep_sergate_plv_28",
        "Low Power",
        ["VIRTPWR", "VPWR", "SLEEP", "VPB"],
    ),
    "sky130_fd_sc_lp__srdlrtp_1": _logic_module(
        "sky130_fd_sc_lp__srdlrtp_1",
        "Low Power",
        ["D", "GATE", "RESET_B", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__srdlstp_1": _logic_module(
        "sky130_fd_sc_lp__srdlstp_1",
        "Low Power",
        ["D", "GATE", "SET_B", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__srdlxtp_1": _logic_module(
        "sky130_fd_sc_lp__srdlxtp_1",
        "Low Power",
        ["D", "GATE", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_lp__sregrbp_1": _logic_module(
        "sky130_fd_sc_lp__sregrbp_1",
        "Low Power",
        ["ASYNC", "CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__sregsbp_1": _logic_module(
        "sky130_fd_sc_lp__sregsbp_1",
        "Low Power",
        ["ASYNC", "CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_lp__srsdfrtn_1": _logic_module(
        "sky130_fd_sc_lp__srsdfrtn_1",
        "Low Power",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SLEEP_B", "KAPWR", "VGND", "VNB"],
    ),
    "sky130_fd_sc_lp__srsdfrtp_1": _logic_module(
        "sky130_fd_sc_lp__srsdfrtp_1",
        "Low Power",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB"],
    ),
    "sky130_fd_sc_lp__srsdfstp_1": _logic_module(
        "sky130_fd_sc_lp__srsdfstp_1",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SET_B", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB"],
    ),
    "sky130_fd_sc_lp__srsdfxtp_1": _logic_module(
        "sky130_fd_sc_lp__srsdfxtp_1",
        "Low Power",
        ["CLK", "D", "SCD", "SCE", "SLEEP_B", "KAPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_lp__tap_1": _logic_module(
        "sky130_fd_sc_lp__tap_1", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__tap_2": _logic_module(
        "sky130_fd_sc_lp__tap_2", "Low Power", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__tapvgnd2_1": _logic_module(
        "sky130_fd_sc_lp__tapvgnd2_1", "Low Power", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__tapvgnd_1": _logic_module(
        "sky130_fd_sc_lp__tapvgnd_1", "Low Power", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_lp__tapvpwrvgnd_1": _logic_module(
        "sky130_fd_sc_lp__tapvpwrvgnd_1", "Low Power", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_lp__xnor2_0": _logic_module(
        "sky130_fd_sc_lp__xnor2_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__xnor2_1": _logic_module(
        "sky130_fd_sc_lp__xnor2_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__xnor2_2": _logic_module(
        "sky130_fd_sc_lp__xnor2_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__xnor2_4": _logic_module(
        "sky130_fd_sc_lp__xnor2_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__xnor2_lp": _logic_module(
        "sky130_fd_sc_lp__xnor2_lp",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__xnor2_m": _logic_module(
        "sky130_fd_sc_lp__xnor2_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_lp__xnor3_1": _logic_module(
        "sky130_fd_sc_lp__xnor3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xnor3_lp": _logic_module(
        "sky130_fd_sc_lp__xnor3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor2_0": _logic_module(
        "sky130_fd_sc_lp__xor2_0",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor2_1": _logic_module(
        "sky130_fd_sc_lp__xor2_1",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor2_2": _logic_module(
        "sky130_fd_sc_lp__xor2_2",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor2_4": _logic_module(
        "sky130_fd_sc_lp__xor2_4",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor2_lp": _logic_module(
        "sky130_fd_sc_lp__xor2_lp",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor2_m": _logic_module(
        "sky130_fd_sc_lp__xor2_m",
        "Low Power",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor3_1": _logic_module(
        "sky130_fd_sc_lp__xor3_1",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_lp__xor3_lp": _logic_module(
        "sky130_fd_sc_lp__xor3_lp",
        "Low Power",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

ls: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_ls__a2bb2o_1": _logic_module(
        "sky130_fd_sc_ls__a2bb2o_1",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a2bb2o_2": _logic_module(
        "sky130_fd_sc_ls__a2bb2o_2",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a2bb2o_4": _logic_module(
        "sky130_fd_sc_ls__a2bb2o_4",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a2bb2oi_1": _logic_module(
        "sky130_fd_sc_ls__a2bb2oi_1",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a2bb2oi_2": _logic_module(
        "sky130_fd_sc_ls__a2bb2oi_2",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a2bb2oi_4": _logic_module(
        "sky130_fd_sc_ls__a2bb2oi_4",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a21bo_1": _logic_module(
        "sky130_fd_sc_ls__a21bo_1",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a21bo_2": _logic_module(
        "sky130_fd_sc_ls__a21bo_2",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a21bo_4": _logic_module(
        "sky130_fd_sc_ls__a21bo_4",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a21boi_1": _logic_module(
        "sky130_fd_sc_ls__a21boi_1",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a21boi_2": _logic_module(
        "sky130_fd_sc_ls__a21boi_2",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a21boi_4": _logic_module(
        "sky130_fd_sc_ls__a21boi_4",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a21o_1": _logic_module(
        "sky130_fd_sc_ls__a21o_1",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a21o_2": _logic_module(
        "sky130_fd_sc_ls__a21o_2",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a21o_4": _logic_module(
        "sky130_fd_sc_ls__a21o_4",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a21oi_1": _logic_module(
        "sky130_fd_sc_ls__a21oi_1",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a21oi_2": _logic_module(
        "sky130_fd_sc_ls__a21oi_2",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a21oi_4": _logic_module(
        "sky130_fd_sc_ls__a21oi_4",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a22o_1": _logic_module(
        "sky130_fd_sc_ls__a22o_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a22o_2": _logic_module(
        "sky130_fd_sc_ls__a22o_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a22o_4": _logic_module(
        "sky130_fd_sc_ls__a22o_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a22oi_1": _logic_module(
        "sky130_fd_sc_ls__a22oi_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a22oi_2": _logic_module(
        "sky130_fd_sc_ls__a22oi_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a22oi_4": _logic_module(
        "sky130_fd_sc_ls__a22oi_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a31o_1": _logic_module(
        "sky130_fd_sc_ls__a31o_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a31o_2": _logic_module(
        "sky130_fd_sc_ls__a31o_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a31o_4": _logic_module(
        "sky130_fd_sc_ls__a31o_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a31oi_1": _logic_module(
        "sky130_fd_sc_ls__a31oi_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a31oi_2": _logic_module(
        "sky130_fd_sc_ls__a31oi_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a31oi_4": _logic_module(
        "sky130_fd_sc_ls__a31oi_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a32o_1": _logic_module(
        "sky130_fd_sc_ls__a32o_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a32o_2": _logic_module(
        "sky130_fd_sc_ls__a32o_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a32o_4": _logic_module(
        "sky130_fd_sc_ls__a32o_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a32oi_1": _logic_module(
        "sky130_fd_sc_ls__a32oi_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a32oi_2": _logic_module(
        "sky130_fd_sc_ls__a32oi_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a32oi_4": _logic_module(
        "sky130_fd_sc_ls__a32oi_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a41o_1": _logic_module(
        "sky130_fd_sc_ls__a41o_1",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a41o_2": _logic_module(
        "sky130_fd_sc_ls__a41o_2",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a41o_4": _logic_module(
        "sky130_fd_sc_ls__a41o_4",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a41oi_1": _logic_module(
        "sky130_fd_sc_ls__a41oi_1",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a41oi_2": _logic_module(
        "sky130_fd_sc_ls__a41oi_2",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a41oi_4": _logic_module(
        "sky130_fd_sc_ls__a41oi_4",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a211o_1": _logic_module(
        "sky130_fd_sc_ls__a211o_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a211o_2": _logic_module(
        "sky130_fd_sc_ls__a211o_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a211o_4": _logic_module(
        "sky130_fd_sc_ls__a211o_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a211oi_1": _logic_module(
        "sky130_fd_sc_ls__a211oi_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a211oi_2": _logic_module(
        "sky130_fd_sc_ls__a211oi_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a211oi_4": _logic_module(
        "sky130_fd_sc_ls__a211oi_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a221o_1": _logic_module(
        "sky130_fd_sc_ls__a221o_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a221o_2": _logic_module(
        "sky130_fd_sc_ls__a221o_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a221o_4": _logic_module(
        "sky130_fd_sc_ls__a221o_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a221oi_1": _logic_module(
        "sky130_fd_sc_ls__a221oi_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a221oi_2": _logic_module(
        "sky130_fd_sc_ls__a221oi_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a221oi_4": _logic_module(
        "sky130_fd_sc_ls__a221oi_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a222o_1": _logic_module(
        "sky130_fd_sc_ls__a222o_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a222o_2": _logic_module(
        "sky130_fd_sc_ls__a222o_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a222oi_1": _logic_module(
        "sky130_fd_sc_ls__a222oi_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a222oi_2": _logic_module(
        "sky130_fd_sc_ls__a222oi_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a311o_1": _logic_module(
        "sky130_fd_sc_ls__a311o_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a311o_2": _logic_module(
        "sky130_fd_sc_ls__a311o_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a311o_4": _logic_module(
        "sky130_fd_sc_ls__a311o_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a311oi_1": _logic_module(
        "sky130_fd_sc_ls__a311oi_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a311oi_2": _logic_module(
        "sky130_fd_sc_ls__a311oi_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a311oi_4": _logic_module(
        "sky130_fd_sc_ls__a311oi_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a2111o_1": _logic_module(
        "sky130_fd_sc_ls__a2111o_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a2111o_2": _logic_module(
        "sky130_fd_sc_ls__a2111o_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a2111o_4": _logic_module(
        "sky130_fd_sc_ls__a2111o_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__a2111oi_1": _logic_module(
        "sky130_fd_sc_ls__a2111oi_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a2111oi_2": _logic_module(
        "sky130_fd_sc_ls__a2111oi_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__a2111oi_4": _logic_module(
        "sky130_fd_sc_ls__a2111oi_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__and2_1": _logic_module(
        "sky130_fd_sc_ls__and2_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and2_2": _logic_module(
        "sky130_fd_sc_ls__and2_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and2_4": _logic_module(
        "sky130_fd_sc_ls__and2_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and2b_1": _logic_module(
        "sky130_fd_sc_ls__and2b_1",
        "Low Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and2b_2": _logic_module(
        "sky130_fd_sc_ls__and2b_2",
        "Low Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and2b_4": _logic_module(
        "sky130_fd_sc_ls__and2b_4",
        "Low Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and3_1": _logic_module(
        "sky130_fd_sc_ls__and3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and3_2": _logic_module(
        "sky130_fd_sc_ls__and3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and3_4": _logic_module(
        "sky130_fd_sc_ls__and3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and3b_1": _logic_module(
        "sky130_fd_sc_ls__and3b_1",
        "Low Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and3b_2": _logic_module(
        "sky130_fd_sc_ls__and3b_2",
        "Low Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and3b_4": _logic_module(
        "sky130_fd_sc_ls__and3b_4",
        "Low Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4_1": _logic_module(
        "sky130_fd_sc_ls__and4_1",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4_2": _logic_module(
        "sky130_fd_sc_ls__and4_2",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4_4": _logic_module(
        "sky130_fd_sc_ls__and4_4",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4b_1": _logic_module(
        "sky130_fd_sc_ls__and4b_1",
        "Low Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4b_2": _logic_module(
        "sky130_fd_sc_ls__and4b_2",
        "Low Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4b_4": _logic_module(
        "sky130_fd_sc_ls__and4b_4",
        "Low Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4bb_1": _logic_module(
        "sky130_fd_sc_ls__and4bb_1",
        "Low Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4bb_2": _logic_module(
        "sky130_fd_sc_ls__and4bb_2",
        "Low Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__and4bb_4": _logic_module(
        "sky130_fd_sc_ls__and4bb_4",
        "Low Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__buf_1": _logic_module(
        "sky130_fd_sc_ls__buf_1", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_ls__buf_2": _logic_module(
        "sky130_fd_sc_ls__buf_2", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_ls__buf_4": _logic_module(
        "sky130_fd_sc_ls__buf_4", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_ls__buf_8": _logic_module(
        "sky130_fd_sc_ls__buf_8", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_ls__buf_16": _logic_module(
        "sky130_fd_sc_ls__buf_16", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "X"]
    ),
    "sky130_fd_sc_ls__bufbuf_8": _logic_module(
        "sky130_fd_sc_ls__bufbuf_8",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__bufbuf_16": _logic_module(
        "sky130_fd_sc_ls__bufbuf_16",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__bufinv_8": _logic_module(
        "sky130_fd_sc_ls__bufinv_8",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__bufinv_16": _logic_module(
        "sky130_fd_sc_ls__bufinv_16",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkbuf_1": _logic_module(
        "sky130_fd_sc_ls__clkbuf_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__clkbuf_2": _logic_module(
        "sky130_fd_sc_ls__clkbuf_2",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__clkbuf_4": _logic_module(
        "sky130_fd_sc_ls__clkbuf_4",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__clkbuf_8": _logic_module(
        "sky130_fd_sc_ls__clkbuf_8",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__clkbuf_16": _logic_module(
        "sky130_fd_sc_ls__clkbuf_16",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__clkdlyinv3sd1_1": _logic_module(
        "sky130_fd_sc_ls__clkdlyinv3sd1_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkdlyinv3sd2_1": _logic_module(
        "sky130_fd_sc_ls__clkdlyinv3sd2_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkdlyinv3sd3_1": _logic_module(
        "sky130_fd_sc_ls__clkdlyinv3sd3_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkdlyinv5sd1_1": _logic_module(
        "sky130_fd_sc_ls__clkdlyinv5sd1_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkdlyinv5sd2_1": _logic_module(
        "sky130_fd_sc_ls__clkdlyinv5sd2_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkdlyinv5sd3_1": _logic_module(
        "sky130_fd_sc_ls__clkdlyinv5sd3_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkinv_1": _logic_module(
        "sky130_fd_sc_ls__clkinv_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkinv_2": _logic_module(
        "sky130_fd_sc_ls__clkinv_2",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkinv_4": _logic_module(
        "sky130_fd_sc_ls__clkinv_4",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkinv_8": _logic_module(
        "sky130_fd_sc_ls__clkinv_8",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__clkinv_16": _logic_module(
        "sky130_fd_sc_ls__clkinv_16",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__conb_1": _logic_module(
        "sky130_fd_sc_ls__conb_1",
        "Low Speed",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_ls__decap_4": _logic_module(
        "sky130_fd_sc_ls__decap_4", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decap_8": _logic_module(
        "sky130_fd_sc_ls__decap_8", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphe_2": _logic_module(
        "sky130_fd_sc_ls__decaphe_2", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphe_3": _logic_module(
        "sky130_fd_sc_ls__decaphe_3", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphe_4": _logic_module(
        "sky130_fd_sc_ls__decaphe_4", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphe_6": _logic_module(
        "sky130_fd_sc_ls__decaphe_6", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphe_8": _logic_module(
        "sky130_fd_sc_ls__decaphe_8", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphe_18": _logic_module(
        "sky130_fd_sc_ls__decaphe_18", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__decaphetap_2": _logic_module(
        "sky130_fd_sc_ls__decaphetap_2", "Low Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__dfbbn_1": _logic_module(
        "sky130_fd_sc_ls__dfbbn_1",
        "Low Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfbbn_2": _logic_module(
        "sky130_fd_sc_ls__dfbbn_2",
        "Low Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfbbp_1": _logic_module(
        "sky130_fd_sc_ls__dfbbp_1",
        "Low Speed",
        ["CLK", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfrbp_1": _logic_module(
        "sky130_fd_sc_ls__dfrbp_1",
        "Low Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfrbp_2": _logic_module(
        "sky130_fd_sc_ls__dfrbp_2",
        "Low Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfrtn_1": _logic_module(
        "sky130_fd_sc_ls__dfrtn_1",
        "Low Speed",
        ["CLK_N", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfrtp_1": _logic_module(
        "sky130_fd_sc_ls__dfrtp_1",
        "Low Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfrtp_2": _logic_module(
        "sky130_fd_sc_ls__dfrtp_2",
        "Low Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfrtp_4": _logic_module(
        "sky130_fd_sc_ls__dfrtp_4",
        "Low Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfsbp_1": _logic_module(
        "sky130_fd_sc_ls__dfsbp_1",
        "Low Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfsbp_2": _logic_module(
        "sky130_fd_sc_ls__dfsbp_2",
        "Low Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfstp_1": _logic_module(
        "sky130_fd_sc_ls__dfstp_1",
        "Low Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfstp_2": _logic_module(
        "sky130_fd_sc_ls__dfstp_2",
        "Low Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfstp_4": _logic_module(
        "sky130_fd_sc_ls__dfstp_4",
        "Low Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfxbp_1": _logic_module(
        "sky130_fd_sc_ls__dfxbp_1",
        "Low Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfxbp_2": _logic_module(
        "sky130_fd_sc_ls__dfxbp_2",
        "Low Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dfxtp_1": _logic_module(
        "sky130_fd_sc_ls__dfxtp_1",
        "Low Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfxtp_2": _logic_module(
        "sky130_fd_sc_ls__dfxtp_2",
        "Low Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dfxtp_4": _logic_module(
        "sky130_fd_sc_ls__dfxtp_4",
        "Low Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__diode_2": _logic_module(
        "sky130_fd_sc_ls__diode_2", "Low Speed", ["DIODE", "VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__dlclkp_1": _logic_module(
        "sky130_fd_sc_ls__dlclkp_1",
        "Low Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ls__dlclkp_2": _logic_module(
        "sky130_fd_sc_ls__dlclkp_2",
        "Low Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ls__dlclkp_4": _logic_module(
        "sky130_fd_sc_ls__dlclkp_4",
        "Low Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ls__dlrbn_1": _logic_module(
        "sky130_fd_sc_ls__dlrbn_1",
        "Low Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlrbn_2": _logic_module(
        "sky130_fd_sc_ls__dlrbn_2",
        "Low Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlrbp_1": _logic_module(
        "sky130_fd_sc_ls__dlrbp_1",
        "Low Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlrbp_2": _logic_module(
        "sky130_fd_sc_ls__dlrbp_2",
        "Low Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlrtn_1": _logic_module(
        "sky130_fd_sc_ls__dlrtn_1",
        "Low Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlrtn_2": _logic_module(
        "sky130_fd_sc_ls__dlrtn_2",
        "Low Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlrtn_4": _logic_module(
        "sky130_fd_sc_ls__dlrtn_4",
        "Low Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlrtp_1": _logic_module(
        "sky130_fd_sc_ls__dlrtp_1",
        "Low Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlrtp_2": _logic_module(
        "sky130_fd_sc_ls__dlrtp_2",
        "Low Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlrtp_4": _logic_module(
        "sky130_fd_sc_ls__dlrtp_4",
        "Low Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlxbn_1": _logic_module(
        "sky130_fd_sc_ls__dlxbn_1",
        "Low Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlxbn_2": _logic_module(
        "sky130_fd_sc_ls__dlxbn_2",
        "Low Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlxbp_1": _logic_module(
        "sky130_fd_sc_ls__dlxbp_1",
        "Low Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__dlxtn_1": _logic_module(
        "sky130_fd_sc_ls__dlxtn_1",
        "Low Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlxtn_2": _logic_module(
        "sky130_fd_sc_ls__dlxtn_2",
        "Low Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlxtn_4": _logic_module(
        "sky130_fd_sc_ls__dlxtn_4",
        "Low Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlxtp_1": _logic_module(
        "sky130_fd_sc_ls__dlxtp_1",
        "Low Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__dlygate4sd1_1": _logic_module(
        "sky130_fd_sc_ls__dlygate4sd1_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__dlygate4sd2_1": _logic_module(
        "sky130_fd_sc_ls__dlygate4sd2_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__dlygate4sd3_1": _logic_module(
        "sky130_fd_sc_ls__dlygate4sd3_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__dlymetal6s2s_1": _logic_module(
        "sky130_fd_sc_ls__dlymetal6s2s_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__dlymetal6s4s_1": _logic_module(
        "sky130_fd_sc_ls__dlymetal6s4s_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__dlymetal6s6s_1": _logic_module(
        "sky130_fd_sc_ls__dlymetal6s6s_1",
        "Low Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__ebufn_1": _logic_module(
        "sky130_fd_sc_ls__ebufn_1",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__ebufn_2": _logic_module(
        "sky130_fd_sc_ls__ebufn_2",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__ebufn_4": _logic_module(
        "sky130_fd_sc_ls__ebufn_4",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__ebufn_8": _logic_module(
        "sky130_fd_sc_ls__ebufn_8",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__edfxbp_1": _logic_module(
        "sky130_fd_sc_ls__edfxbp_1",
        "Low Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__edfxtp_1": _logic_module(
        "sky130_fd_sc_ls__edfxtp_1",
        "Low Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__einvn_1": _logic_module(
        "sky130_fd_sc_ls__einvn_1",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvn_2": _logic_module(
        "sky130_fd_sc_ls__einvn_2",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvn_4": _logic_module(
        "sky130_fd_sc_ls__einvn_4",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvn_8": _logic_module(
        "sky130_fd_sc_ls__einvn_8",
        "Low Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvp_1": _logic_module(
        "sky130_fd_sc_ls__einvp_1",
        "Low Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvp_2": _logic_module(
        "sky130_fd_sc_ls__einvp_2",
        "Low Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvp_4": _logic_module(
        "sky130_fd_sc_ls__einvp_4",
        "Low Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__einvp_8": _logic_module(
        "sky130_fd_sc_ls__einvp_8",
        "Low Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ls__fa_1": _logic_module(
        "sky130_fd_sc_ls__fa_1",
        "Low Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fa_2": _logic_module(
        "sky130_fd_sc_ls__fa_2",
        "Low Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fa_4": _logic_module(
        "sky130_fd_sc_ls__fa_4",
        "Low Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fah_1": _logic_module(
        "sky130_fd_sc_ls__fah_1",
        "Low Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fah_2": _logic_module(
        "sky130_fd_sc_ls__fah_2",
        "Low Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fah_4": _logic_module(
        "sky130_fd_sc_ls__fah_4",
        "Low Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fahcin_1": _logic_module(
        "sky130_fd_sc_ls__fahcin_1",
        "Low Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__fahcon_1": _logic_module(
        "sky130_fd_sc_ls__fahcon_1",
        "Low Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT_N", "SUM"],
    ),
    "sky130_fd_sc_ls__fill_1": _logic_module(
        "sky130_fd_sc_ls__fill_1", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__fill_2": _logic_module(
        "sky130_fd_sc_ls__fill_2", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__fill_4": _logic_module(
        "sky130_fd_sc_ls__fill_4", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__fill_8": _logic_module(
        "sky130_fd_sc_ls__fill_8", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__fill_diode_2": _logic_module(
        "sky130_fd_sc_ls__fill_diode_2", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__fill_diode_4": _logic_module(
        "sky130_fd_sc_ls__fill_diode_4", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__fill_diode_8": _logic_module(
        "sky130_fd_sc_ls__fill_diode_8", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__ha_1": _logic_module(
        "sky130_fd_sc_ls__ha_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__ha_2": _logic_module(
        "sky130_fd_sc_ls__ha_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__ha_4": _logic_module(
        "sky130_fd_sc_ls__ha_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ls__inv_1": _logic_module(
        "sky130_fd_sc_ls__inv_1", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_ls__inv_2": _logic_module(
        "sky130_fd_sc_ls__inv_2", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_ls__inv_4": _logic_module(
        "sky130_fd_sc_ls__inv_4", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_ls__inv_8": _logic_module(
        "sky130_fd_sc_ls__inv_8", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_ls__inv_16": _logic_module(
        "sky130_fd_sc_ls__inv_16", "Low Speed", ["A", "VGND", "VNB", "VPB", "VPWR", "Y"]
    ),
    "sky130_fd_sc_ls__latchupcell": _logic_module(
        "sky130_fd_sc_ls__latchupcell", "Low Speed", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_ls__maj3_1": _logic_module(
        "sky130_fd_sc_ls__maj3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__maj3_2": _logic_module(
        "sky130_fd_sc_ls__maj3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__maj3_4": _logic_module(
        "sky130_fd_sc_ls__maj3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__mux2_1": _logic_module(
        "sky130_fd_sc_ls__mux2_1",
        "Low Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__mux2_2": _logic_module(
        "sky130_fd_sc_ls__mux2_2",
        "Low Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__mux2_4": _logic_module(
        "sky130_fd_sc_ls__mux2_4",
        "Low Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__mux2i_1": _logic_module(
        "sky130_fd_sc_ls__mux2i_1",
        "Low Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__mux2i_2": _logic_module(
        "sky130_fd_sc_ls__mux2i_2",
        "Low Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__mux2i_4": _logic_module(
        "sky130_fd_sc_ls__mux2i_4",
        "Low Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__mux4_1": _logic_module(
        "sky130_fd_sc_ls__mux4_1",
        "Low Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__mux4_2": _logic_module(
        "sky130_fd_sc_ls__mux4_2",
        "Low Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__mux4_4": _logic_module(
        "sky130_fd_sc_ls__mux4_4",
        "Low Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__nand2_1": _logic_module(
        "sky130_fd_sc_ls__nand2_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand2_2": _logic_module(
        "sky130_fd_sc_ls__nand2_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand2_4": _logic_module(
        "sky130_fd_sc_ls__nand2_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand2_8": _logic_module(
        "sky130_fd_sc_ls__nand2_8",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand2b_1": _logic_module(
        "sky130_fd_sc_ls__nand2b_1",
        "Low Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand2b_2": _logic_module(
        "sky130_fd_sc_ls__nand2b_2",
        "Low Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand2b_4": _logic_module(
        "sky130_fd_sc_ls__nand2b_4",
        "Low Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand3_1": _logic_module(
        "sky130_fd_sc_ls__nand3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand3_2": _logic_module(
        "sky130_fd_sc_ls__nand3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand3_4": _logic_module(
        "sky130_fd_sc_ls__nand3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand3b_1": _logic_module(
        "sky130_fd_sc_ls__nand3b_1",
        "Low Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand3b_2": _logic_module(
        "sky130_fd_sc_ls__nand3b_2",
        "Low Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand3b_4": _logic_module(
        "sky130_fd_sc_ls__nand3b_4",
        "Low Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4_1": _logic_module(
        "sky130_fd_sc_ls__nand4_1",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4_2": _logic_module(
        "sky130_fd_sc_ls__nand4_2",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4_4": _logic_module(
        "sky130_fd_sc_ls__nand4_4",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4b_1": _logic_module(
        "sky130_fd_sc_ls__nand4b_1",
        "Low Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4b_2": _logic_module(
        "sky130_fd_sc_ls__nand4b_2",
        "Low Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4b_4": _logic_module(
        "sky130_fd_sc_ls__nand4b_4",
        "Low Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4bb_1": _logic_module(
        "sky130_fd_sc_ls__nand4bb_1",
        "Low Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4bb_2": _logic_module(
        "sky130_fd_sc_ls__nand4bb_2",
        "Low Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nand4bb_4": _logic_module(
        "sky130_fd_sc_ls__nand4bb_4",
        "Low Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2_1": _logic_module(
        "sky130_fd_sc_ls__nor2_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2_2": _logic_module(
        "sky130_fd_sc_ls__nor2_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2_4": _logic_module(
        "sky130_fd_sc_ls__nor2_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2_8": _logic_module(
        "sky130_fd_sc_ls__nor2_8",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2b_1": _logic_module(
        "sky130_fd_sc_ls__nor2b_1",
        "Low Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2b_2": _logic_module(
        "sky130_fd_sc_ls__nor2b_2",
        "Low Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor2b_4": _logic_module(
        "sky130_fd_sc_ls__nor2b_4",
        "Low Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor3_1": _logic_module(
        "sky130_fd_sc_ls__nor3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor3_2": _logic_module(
        "sky130_fd_sc_ls__nor3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor3_4": _logic_module(
        "sky130_fd_sc_ls__nor3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor3b_1": _logic_module(
        "sky130_fd_sc_ls__nor3b_1",
        "Low Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor3b_2": _logic_module(
        "sky130_fd_sc_ls__nor3b_2",
        "Low Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor3b_4": _logic_module(
        "sky130_fd_sc_ls__nor3b_4",
        "Low Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4_1": _logic_module(
        "sky130_fd_sc_ls__nor4_1",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4_2": _logic_module(
        "sky130_fd_sc_ls__nor4_2",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4_4": _logic_module(
        "sky130_fd_sc_ls__nor4_4",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4b_1": _logic_module(
        "sky130_fd_sc_ls__nor4b_1",
        "Low Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4b_2": _logic_module(
        "sky130_fd_sc_ls__nor4b_2",
        "Low Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4b_4": _logic_module(
        "sky130_fd_sc_ls__nor4b_4",
        "Low Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4bb_1": _logic_module(
        "sky130_fd_sc_ls__nor4bb_1",
        "Low Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4bb_2": _logic_module(
        "sky130_fd_sc_ls__nor4bb_2",
        "Low Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__nor4bb_4": _logic_module(
        "sky130_fd_sc_ls__nor4bb_4",
        "Low Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o2bb2a_1": _logic_module(
        "sky130_fd_sc_ls__o2bb2a_1",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o2bb2a_2": _logic_module(
        "sky130_fd_sc_ls__o2bb2a_2",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o2bb2a_4": _logic_module(
        "sky130_fd_sc_ls__o2bb2a_4",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o2bb2ai_1": _logic_module(
        "sky130_fd_sc_ls__o2bb2ai_1",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o2bb2ai_2": _logic_module(
        "sky130_fd_sc_ls__o2bb2ai_2",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o2bb2ai_4": _logic_module(
        "sky130_fd_sc_ls__o2bb2ai_4",
        "Low Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o21a_1": _logic_module(
        "sky130_fd_sc_ls__o21a_1",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o21a_2": _logic_module(
        "sky130_fd_sc_ls__o21a_2",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o21a_4": _logic_module(
        "sky130_fd_sc_ls__o21a_4",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o21ai_1": _logic_module(
        "sky130_fd_sc_ls__o21ai_1",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o21ai_2": _logic_module(
        "sky130_fd_sc_ls__o21ai_2",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o21ai_4": _logic_module(
        "sky130_fd_sc_ls__o21ai_4",
        "Low Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o21ba_1": _logic_module(
        "sky130_fd_sc_ls__o21ba_1",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o21ba_2": _logic_module(
        "sky130_fd_sc_ls__o21ba_2",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o21ba_4": _logic_module(
        "sky130_fd_sc_ls__o21ba_4",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o21bai_1": _logic_module(
        "sky130_fd_sc_ls__o21bai_1",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o21bai_2": _logic_module(
        "sky130_fd_sc_ls__o21bai_2",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o21bai_4": _logic_module(
        "sky130_fd_sc_ls__o21bai_4",
        "Low Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o22a_1": _logic_module(
        "sky130_fd_sc_ls__o22a_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o22a_2": _logic_module(
        "sky130_fd_sc_ls__o22a_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o22a_4": _logic_module(
        "sky130_fd_sc_ls__o22a_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o22ai_1": _logic_module(
        "sky130_fd_sc_ls__o22ai_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o22ai_2": _logic_module(
        "sky130_fd_sc_ls__o22ai_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o22ai_4": _logic_module(
        "sky130_fd_sc_ls__o22ai_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o31a_1": _logic_module(
        "sky130_fd_sc_ls__o31a_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o31a_2": _logic_module(
        "sky130_fd_sc_ls__o31a_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o31a_4": _logic_module(
        "sky130_fd_sc_ls__o31a_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o31ai_1": _logic_module(
        "sky130_fd_sc_ls__o31ai_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o31ai_2": _logic_module(
        "sky130_fd_sc_ls__o31ai_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o31ai_4": _logic_module(
        "sky130_fd_sc_ls__o31ai_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o32a_1": _logic_module(
        "sky130_fd_sc_ls__o32a_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o32a_2": _logic_module(
        "sky130_fd_sc_ls__o32a_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o32a_4": _logic_module(
        "sky130_fd_sc_ls__o32a_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o32ai_1": _logic_module(
        "sky130_fd_sc_ls__o32ai_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o32ai_2": _logic_module(
        "sky130_fd_sc_ls__o32ai_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o32ai_4": _logic_module(
        "sky130_fd_sc_ls__o32ai_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o41a_1": _logic_module(
        "sky130_fd_sc_ls__o41a_1",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o41a_2": _logic_module(
        "sky130_fd_sc_ls__o41a_2",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o41a_4": _logic_module(
        "sky130_fd_sc_ls__o41a_4",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o41ai_1": _logic_module(
        "sky130_fd_sc_ls__o41ai_1",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o41ai_2": _logic_module(
        "sky130_fd_sc_ls__o41ai_2",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o41ai_4": _logic_module(
        "sky130_fd_sc_ls__o41ai_4",
        "Low Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o211a_1": _logic_module(
        "sky130_fd_sc_ls__o211a_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o211a_2": _logic_module(
        "sky130_fd_sc_ls__o211a_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o211a_4": _logic_module(
        "sky130_fd_sc_ls__o211a_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o211ai_1": _logic_module(
        "sky130_fd_sc_ls__o211ai_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o211ai_2": _logic_module(
        "sky130_fd_sc_ls__o211ai_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o211ai_4": _logic_module(
        "sky130_fd_sc_ls__o211ai_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o221a_1": _logic_module(
        "sky130_fd_sc_ls__o221a_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o221a_2": _logic_module(
        "sky130_fd_sc_ls__o221a_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o221a_4": _logic_module(
        "sky130_fd_sc_ls__o221a_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o221ai_1": _logic_module(
        "sky130_fd_sc_ls__o221ai_1",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o221ai_2": _logic_module(
        "sky130_fd_sc_ls__o221ai_2",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o221ai_4": _logic_module(
        "sky130_fd_sc_ls__o221ai_4",
        "Low Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o311a_1": _logic_module(
        "sky130_fd_sc_ls__o311a_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o311a_2": _logic_module(
        "sky130_fd_sc_ls__o311a_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o311a_4": _logic_module(
        "sky130_fd_sc_ls__o311a_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o311ai_1": _logic_module(
        "sky130_fd_sc_ls__o311ai_1",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o311ai_2": _logic_module(
        "sky130_fd_sc_ls__o311ai_2",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o311ai_4": _logic_module(
        "sky130_fd_sc_ls__o311ai_4",
        "Low Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o2111a_1": _logic_module(
        "sky130_fd_sc_ls__o2111a_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o2111a_2": _logic_module(
        "sky130_fd_sc_ls__o2111a_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o2111a_4": _logic_module(
        "sky130_fd_sc_ls__o2111a_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__o2111ai_1": _logic_module(
        "sky130_fd_sc_ls__o2111ai_1",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o2111ai_2": _logic_module(
        "sky130_fd_sc_ls__o2111ai_2",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__o2111ai_4": _logic_module(
        "sky130_fd_sc_ls__o2111ai_4",
        "Low Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__or2_1": _logic_module(
        "sky130_fd_sc_ls__or2_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or2_2": _logic_module(
        "sky130_fd_sc_ls__or2_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or2_4": _logic_module(
        "sky130_fd_sc_ls__or2_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or2b_1": _logic_module(
        "sky130_fd_sc_ls__or2b_1",
        "Low Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or2b_2": _logic_module(
        "sky130_fd_sc_ls__or2b_2",
        "Low Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or2b_4": _logic_module(
        "sky130_fd_sc_ls__or2b_4",
        "Low Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or3_1": _logic_module(
        "sky130_fd_sc_ls__or3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or3_2": _logic_module(
        "sky130_fd_sc_ls__or3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or3_4": _logic_module(
        "sky130_fd_sc_ls__or3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or3b_1": _logic_module(
        "sky130_fd_sc_ls__or3b_1",
        "Low Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or3b_2": _logic_module(
        "sky130_fd_sc_ls__or3b_2",
        "Low Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or3b_4": _logic_module(
        "sky130_fd_sc_ls__or3b_4",
        "Low Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4_1": _logic_module(
        "sky130_fd_sc_ls__or4_1",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4_2": _logic_module(
        "sky130_fd_sc_ls__or4_2",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4_4": _logic_module(
        "sky130_fd_sc_ls__or4_4",
        "Low Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4b_1": _logic_module(
        "sky130_fd_sc_ls__or4b_1",
        "Low Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4b_2": _logic_module(
        "sky130_fd_sc_ls__or4b_2",
        "Low Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4b_4": _logic_module(
        "sky130_fd_sc_ls__or4b_4",
        "Low Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4bb_1": _logic_module(
        "sky130_fd_sc_ls__or4bb_1",
        "Low Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4bb_2": _logic_module(
        "sky130_fd_sc_ls__or4bb_2",
        "Low Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__or4bb_4": _logic_module(
        "sky130_fd_sc_ls__or4bb_4",
        "Low Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__sdfbbn_1": _logic_module(
        "sky130_fd_sc_ls__sdfbbn_1",
        "Low Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_ls__sdfbbn_2": _logic_module(
        "sky130_fd_sc_ls__sdfbbn_2",
        "Low Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_ls__sdfbbp_1": _logic_module(
        "sky130_fd_sc_ls__sdfbbp_1",
        "Low Speed",
        [
            "CLK",
            "D",
            "RESET_B",
            "SCD",
            "SCE",
            "SET_B",
            "VGND",
            "VNB",
            "VPB",
            "VPWR",
            "Q",
        ],
    ),
    "sky130_fd_sc_ls__sdfrbp_1": _logic_module(
        "sky130_fd_sc_ls__sdfrbp_1",
        "Low Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sdfrbp_2": _logic_module(
        "sky130_fd_sc_ls__sdfrbp_2",
        "Low Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sdfrtn_1": _logic_module(
        "sky130_fd_sc_ls__sdfrtn_1",
        "Low Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfrtp_1": _logic_module(
        "sky130_fd_sc_ls__sdfrtp_1",
        "Low Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfrtp_2": _logic_module(
        "sky130_fd_sc_ls__sdfrtp_2",
        "Low Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfrtp_4": _logic_module(
        "sky130_fd_sc_ls__sdfrtp_4",
        "Low Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfsbp_1": _logic_module(
        "sky130_fd_sc_ls__sdfsbp_1",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sdfsbp_2": _logic_module(
        "sky130_fd_sc_ls__sdfsbp_2",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sdfstp_1": _logic_module(
        "sky130_fd_sc_ls__sdfstp_1",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfstp_2": _logic_module(
        "sky130_fd_sc_ls__sdfstp_2",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfstp_4": _logic_module(
        "sky130_fd_sc_ls__sdfstp_4",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfxbp_1": _logic_module(
        "sky130_fd_sc_ls__sdfxbp_1",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sdfxbp_2": _logic_module(
        "sky130_fd_sc_ls__sdfxbp_2",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sdfxtp_1": _logic_module(
        "sky130_fd_sc_ls__sdfxtp_1",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfxtp_2": _logic_module(
        "sky130_fd_sc_ls__sdfxtp_2",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdfxtp_4": _logic_module(
        "sky130_fd_sc_ls__sdfxtp_4",
        "Low Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sdlclkp_1": _logic_module(
        "sky130_fd_sc_ls__sdlclkp_1",
        "Low Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ls__sdlclkp_2": _logic_module(
        "sky130_fd_sc_ls__sdlclkp_2",
        "Low Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ls__sdlclkp_4": _logic_module(
        "sky130_fd_sc_ls__sdlclkp_4",
        "Low Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ls__sedfxbp_1": _logic_module(
        "sky130_fd_sc_ls__sedfxbp_1",
        "Low Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sedfxbp_2": _logic_module(
        "sky130_fd_sc_ls__sedfxbp_2",
        "Low Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ls__sedfxtp_1": _logic_module(
        "sky130_fd_sc_ls__sedfxtp_1",
        "Low Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sedfxtp_2": _logic_module(
        "sky130_fd_sc_ls__sedfxtp_2",
        "Low Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__sedfxtp_4": _logic_module(
        "sky130_fd_sc_ls__sedfxtp_4",
        "Low Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ls__tap_1": _logic_module(
        "sky130_fd_sc_ls__tap_1", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__tap_2": _logic_module(
        "sky130_fd_sc_ls__tap_2", "Low Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__tapmet1_2": _logic_module(
        "sky130_fd_sc_ls__tapmet1_2", "Low Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__tapvgnd2_1": _logic_module(
        "sky130_fd_sc_ls__tapvgnd2_1", "Low Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__tapvgnd_1": _logic_module(
        "sky130_fd_sc_ls__tapvgnd_1", "Low Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ls__tapvgndnovpb_1": _logic_module(
        "sky130_fd_sc_ls__tapvgndnovpb_1", "Low Speed", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_ls__tapvpwrvgnd_1": _logic_module(
        "sky130_fd_sc_ls__tapvpwrvgnd_1", "Low Speed", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_ls__xnor2_1": _logic_module(
        "sky130_fd_sc_ls__xnor2_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__xnor2_2": _logic_module(
        "sky130_fd_sc_ls__xnor2_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__xnor2_4": _logic_module(
        "sky130_fd_sc_ls__xnor2_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ls__xnor3_1": _logic_module(
        "sky130_fd_sc_ls__xnor3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xnor3_2": _logic_module(
        "sky130_fd_sc_ls__xnor3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xnor3_4": _logic_module(
        "sky130_fd_sc_ls__xnor3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xor2_1": _logic_module(
        "sky130_fd_sc_ls__xor2_1",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xor2_2": _logic_module(
        "sky130_fd_sc_ls__xor2_2",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xor2_4": _logic_module(
        "sky130_fd_sc_ls__xor2_4",
        "Low Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xor3_1": _logic_module(
        "sky130_fd_sc_ls__xor3_1",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xor3_2": _logic_module(
        "sky130_fd_sc_ls__xor3_2",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ls__xor3_4": _logic_module(
        "sky130_fd_sc_ls__xor3_4",
        "Low Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

ms: Dict[str, h.ExternalModule] = {
    "sky130_fd_sc_ms__a2bb2o_1": _logic_module(
        "sky130_fd_sc_ms__a2bb2o_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a2bb2o_2": _logic_module(
        "sky130_fd_sc_ms__a2bb2o_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a2bb2o_4": _logic_module(
        "sky130_fd_sc_ms__a2bb2o_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a2bb2oi_1": _logic_module(
        "sky130_fd_sc_ms__a2bb2oi_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a2bb2oi_2": _logic_module(
        "sky130_fd_sc_ms__a2bb2oi_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a2bb2oi_4": _logic_module(
        "sky130_fd_sc_ms__a2bb2oi_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a21bo_1": _logic_module(
        "sky130_fd_sc_ms__a21bo_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a21bo_2": _logic_module(
        "sky130_fd_sc_ms__a21bo_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a21bo_4": _logic_module(
        "sky130_fd_sc_ms__a21bo_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a21boi_1": _logic_module(
        "sky130_fd_sc_ms__a21boi_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a21boi_2": _logic_module(
        "sky130_fd_sc_ms__a21boi_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a21boi_4": _logic_module(
        "sky130_fd_sc_ms__a21boi_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a21o_1": _logic_module(
        "sky130_fd_sc_ms__a21o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a21o_2": _logic_module(
        "sky130_fd_sc_ms__a21o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a21o_4": _logic_module(
        "sky130_fd_sc_ms__a21o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a21oi_1": _logic_module(
        "sky130_fd_sc_ms__a21oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a21oi_2": _logic_module(
        "sky130_fd_sc_ms__a21oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a21oi_4": _logic_module(
        "sky130_fd_sc_ms__a21oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a22o_1": _logic_module(
        "sky130_fd_sc_ms__a22o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a22o_2": _logic_module(
        "sky130_fd_sc_ms__a22o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a22o_4": _logic_module(
        "sky130_fd_sc_ms__a22o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a22oi_1": _logic_module(
        "sky130_fd_sc_ms__a22oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a22oi_2": _logic_module(
        "sky130_fd_sc_ms__a22oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a22oi_4": _logic_module(
        "sky130_fd_sc_ms__a22oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a31o_1": _logic_module(
        "sky130_fd_sc_ms__a31o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a31o_2": _logic_module(
        "sky130_fd_sc_ms__a31o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a31o_4": _logic_module(
        "sky130_fd_sc_ms__a31o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a31oi_1": _logic_module(
        "sky130_fd_sc_ms__a31oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a31oi_2": _logic_module(
        "sky130_fd_sc_ms__a31oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a31oi_4": _logic_module(
        "sky130_fd_sc_ms__a31oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a32o_1": _logic_module(
        "sky130_fd_sc_ms__a32o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a32o_2": _logic_module(
        "sky130_fd_sc_ms__a32o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a32o_4": _logic_module(
        "sky130_fd_sc_ms__a32o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a32oi_1": _logic_module(
        "sky130_fd_sc_ms__a32oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a32oi_2": _logic_module(
        "sky130_fd_sc_ms__a32oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a32oi_4": _logic_module(
        "sky130_fd_sc_ms__a32oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a41o_1": _logic_module(
        "sky130_fd_sc_ms__a41o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a41o_2": _logic_module(
        "sky130_fd_sc_ms__a41o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a41o_4": _logic_module(
        "sky130_fd_sc_ms__a41o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a41oi_1": _logic_module(
        "sky130_fd_sc_ms__a41oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a41oi_2": _logic_module(
        "sky130_fd_sc_ms__a41oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a41oi_4": _logic_module(
        "sky130_fd_sc_ms__a41oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a211o_1": _logic_module(
        "sky130_fd_sc_ms__a211o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a211o_2": _logic_module(
        "sky130_fd_sc_ms__a211o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a211o_4": _logic_module(
        "sky130_fd_sc_ms__a211o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a211oi_1": _logic_module(
        "sky130_fd_sc_ms__a211oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a211oi_2": _logic_module(
        "sky130_fd_sc_ms__a211oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a211oi_4": _logic_module(
        "sky130_fd_sc_ms__a211oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a221o_1": _logic_module(
        "sky130_fd_sc_ms__a221o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a221o_2": _logic_module(
        "sky130_fd_sc_ms__a221o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a221o_4": _logic_module(
        "sky130_fd_sc_ms__a221o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a221oi_1": _logic_module(
        "sky130_fd_sc_ms__a221oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a221oi_2": _logic_module(
        "sky130_fd_sc_ms__a221oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a221oi_4": _logic_module(
        "sky130_fd_sc_ms__a221oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a222o_1": _logic_module(
        "sky130_fd_sc_ms__a222o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a222o_2": _logic_module(
        "sky130_fd_sc_ms__a222o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a222oi_1": _logic_module(
        "sky130_fd_sc_ms__a222oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a222oi_2": _logic_module(
        "sky130_fd_sc_ms__a222oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a311o_1": _logic_module(
        "sky130_fd_sc_ms__a311o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a311o_2": _logic_module(
        "sky130_fd_sc_ms__a311o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a311o_4": _logic_module(
        "sky130_fd_sc_ms__a311o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a311oi_1": _logic_module(
        "sky130_fd_sc_ms__a311oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a311oi_2": _logic_module(
        "sky130_fd_sc_ms__a311oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a311oi_4": _logic_module(
        "sky130_fd_sc_ms__a311oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a2111o_1": _logic_module(
        "sky130_fd_sc_ms__a2111o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a2111o_2": _logic_module(
        "sky130_fd_sc_ms__a2111o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a2111o_4": _logic_module(
        "sky130_fd_sc_ms__a2111o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__a2111oi_1": _logic_module(
        "sky130_fd_sc_ms__a2111oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a2111oi_2": _logic_module(
        "sky130_fd_sc_ms__a2111oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__a2111oi_4": _logic_module(
        "sky130_fd_sc_ms__a2111oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__and2_1": _logic_module(
        "sky130_fd_sc_ms__and2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and2_2": _logic_module(
        "sky130_fd_sc_ms__and2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and2_4": _logic_module(
        "sky130_fd_sc_ms__and2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and2b_1": _logic_module(
        "sky130_fd_sc_ms__and2b_1",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and2b_2": _logic_module(
        "sky130_fd_sc_ms__and2b_2",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and2b_4": _logic_module(
        "sky130_fd_sc_ms__and2b_4",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and3_1": _logic_module(
        "sky130_fd_sc_ms__and3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and3_2": _logic_module(
        "sky130_fd_sc_ms__and3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and3_4": _logic_module(
        "sky130_fd_sc_ms__and3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and3b_1": _logic_module(
        "sky130_fd_sc_ms__and3b_1",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and3b_2": _logic_module(
        "sky130_fd_sc_ms__and3b_2",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and3b_4": _logic_module(
        "sky130_fd_sc_ms__and3b_4",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4_1": _logic_module(
        "sky130_fd_sc_ms__and4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4_2": _logic_module(
        "sky130_fd_sc_ms__and4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4_4": _logic_module(
        "sky130_fd_sc_ms__and4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4b_1": _logic_module(
        "sky130_fd_sc_ms__and4b_1",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4b_2": _logic_module(
        "sky130_fd_sc_ms__and4b_2",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4b_4": _logic_module(
        "sky130_fd_sc_ms__and4b_4",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4bb_1": _logic_module(
        "sky130_fd_sc_ms__and4bb_1",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4bb_2": _logic_module(
        "sky130_fd_sc_ms__and4bb_2",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__and4bb_4": _logic_module(
        "sky130_fd_sc_ms__and4bb_4",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__buf_1": _logic_module(
        "sky130_fd_sc_ms__buf_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__buf_2": _logic_module(
        "sky130_fd_sc_ms__buf_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__buf_4": _logic_module(
        "sky130_fd_sc_ms__buf_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__buf_8": _logic_module(
        "sky130_fd_sc_ms__buf_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__buf_16": _logic_module(
        "sky130_fd_sc_ms__buf_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__bufbuf_8": _logic_module(
        "sky130_fd_sc_ms__bufbuf_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__bufbuf_16": _logic_module(
        "sky130_fd_sc_ms__bufbuf_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__bufinv_8": _logic_module(
        "sky130_fd_sc_ms__bufinv_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__bufinv_16": _logic_module(
        "sky130_fd_sc_ms__bufinv_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkbuf_1": _logic_module(
        "sky130_fd_sc_ms__clkbuf_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__clkbuf_2": _logic_module(
        "sky130_fd_sc_ms__clkbuf_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__clkbuf_4": _logic_module(
        "sky130_fd_sc_ms__clkbuf_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__clkbuf_8": _logic_module(
        "sky130_fd_sc_ms__clkbuf_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__clkbuf_16": _logic_module(
        "sky130_fd_sc_ms__clkbuf_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__clkdlyinv3sd1_1": _logic_module(
        "sky130_fd_sc_ms__clkdlyinv3sd1_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkdlyinv3sd2_1": _logic_module(
        "sky130_fd_sc_ms__clkdlyinv3sd2_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkdlyinv3sd3_1": _logic_module(
        "sky130_fd_sc_ms__clkdlyinv3sd3_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkdlyinv5sd1_1": _logic_module(
        "sky130_fd_sc_ms__clkdlyinv5sd1_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkdlyinv5sd2_1": _logic_module(
        "sky130_fd_sc_ms__clkdlyinv5sd2_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkdlyinv5sd3_1": _logic_module(
        "sky130_fd_sc_ms__clkdlyinv5sd3_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkinv_1": _logic_module(
        "sky130_fd_sc_ms__clkinv_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkinv_2": _logic_module(
        "sky130_fd_sc_ms__clkinv_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkinv_4": _logic_module(
        "sky130_fd_sc_ms__clkinv_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkinv_8": _logic_module(
        "sky130_fd_sc_ms__clkinv_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__clkinv_16": _logic_module(
        "sky130_fd_sc_ms__clkinv_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__conb_1": _logic_module(
        "sky130_fd_sc_ms__conb_1",
        "Medium Speed",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "sky130_fd_sc_ms__decap_4": _logic_module(
        "sky130_fd_sc_ms__decap_4", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__decap_8": _logic_module(
        "sky130_fd_sc_ms__decap_8", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__dfbbn_1": _logic_module(
        "sky130_fd_sc_ms__dfbbn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfbbn_2": _logic_module(
        "sky130_fd_sc_ms__dfbbn_2",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfbbp_1": _logic_module(
        "sky130_fd_sc_ms__dfbbp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfrbp_1": _logic_module(
        "sky130_fd_sc_ms__dfrbp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfrbp_2": _logic_module(
        "sky130_fd_sc_ms__dfrbp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfrtn_1": _logic_module(
        "sky130_fd_sc_ms__dfrtn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfrtp_1": _logic_module(
        "sky130_fd_sc_ms__dfrtp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfrtp_2": _logic_module(
        "sky130_fd_sc_ms__dfrtp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfrtp_4": _logic_module(
        "sky130_fd_sc_ms__dfrtp_4",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfsbp_1": _logic_module(
        "sky130_fd_sc_ms__dfsbp_1",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfsbp_2": _logic_module(
        "sky130_fd_sc_ms__dfsbp_2",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfstp_1": _logic_module(
        "sky130_fd_sc_ms__dfstp_1",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfstp_2": _logic_module(
        "sky130_fd_sc_ms__dfstp_2",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfstp_4": _logic_module(
        "sky130_fd_sc_ms__dfstp_4",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfxbp_1": _logic_module(
        "sky130_fd_sc_ms__dfxbp_1",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfxbp_2": _logic_module(
        "sky130_fd_sc_ms__dfxbp_2",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dfxtp_1": _logic_module(
        "sky130_fd_sc_ms__dfxtp_1",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfxtp_2": _logic_module(
        "sky130_fd_sc_ms__dfxtp_2",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dfxtp_4": _logic_module(
        "sky130_fd_sc_ms__dfxtp_4",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__diode_2": _logic_module(
        "sky130_fd_sc_ms__diode_2",
        "Medium Speed",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_ms__dlclkp_1": _logic_module(
        "sky130_fd_sc_ms__dlclkp_1",
        "Medium Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ms__dlclkp_2": _logic_module(
        "sky130_fd_sc_ms__dlclkp_2",
        "Medium Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ms__dlclkp_4": _logic_module(
        "sky130_fd_sc_ms__dlclkp_4",
        "Medium Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ms__dlrbn_1": _logic_module(
        "sky130_fd_sc_ms__dlrbn_1",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlrbn_2": _logic_module(
        "sky130_fd_sc_ms__dlrbn_2",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlrbp_1": _logic_module(
        "sky130_fd_sc_ms__dlrbp_1",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlrbp_2": _logic_module(
        "sky130_fd_sc_ms__dlrbp_2",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlrtn_1": _logic_module(
        "sky130_fd_sc_ms__dlrtn_1",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlrtn_2": _logic_module(
        "sky130_fd_sc_ms__dlrtn_2",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlrtn_4": _logic_module(
        "sky130_fd_sc_ms__dlrtn_4",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlrtp_1": _logic_module(
        "sky130_fd_sc_ms__dlrtp_1",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlrtp_2": _logic_module(
        "sky130_fd_sc_ms__dlrtp_2",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlrtp_4": _logic_module(
        "sky130_fd_sc_ms__dlrtp_4",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlxbn_1": _logic_module(
        "sky130_fd_sc_ms__dlxbn_1",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlxbn_2": _logic_module(
        "sky130_fd_sc_ms__dlxbn_2",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlxbp_1": _logic_module(
        "sky130_fd_sc_ms__dlxbp_1",
        "Medium Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__dlxtn_1": _logic_module(
        "sky130_fd_sc_ms__dlxtn_1",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlxtn_2": _logic_module(
        "sky130_fd_sc_ms__dlxtn_2",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlxtn_4": _logic_module(
        "sky130_fd_sc_ms__dlxtn_4",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlxtp_1": _logic_module(
        "sky130_fd_sc_ms__dlxtp_1",
        "Medium Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__dlygate4sd1_1": _logic_module(
        "sky130_fd_sc_ms__dlygate4sd1_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__dlygate4sd2_1": _logic_module(
        "sky130_fd_sc_ms__dlygate4sd2_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__dlygate4sd3_1": _logic_module(
        "sky130_fd_sc_ms__dlygate4sd3_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__dlymetal6s2s_1": _logic_module(
        "sky130_fd_sc_ms__dlymetal6s2s_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__dlymetal6s4s_1": _logic_module(
        "sky130_fd_sc_ms__dlymetal6s4s_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__dlymetal6s6s_1": _logic_module(
        "sky130_fd_sc_ms__dlymetal6s6s_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__ebufn_1": _logic_module(
        "sky130_fd_sc_ms__ebufn_1",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__ebufn_2": _logic_module(
        "sky130_fd_sc_ms__ebufn_2",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__ebufn_4": _logic_module(
        "sky130_fd_sc_ms__ebufn_4",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__ebufn_8": _logic_module(
        "sky130_fd_sc_ms__ebufn_8",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__edfxbp_1": _logic_module(
        "sky130_fd_sc_ms__edfxbp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__edfxtp_1": _logic_module(
        "sky130_fd_sc_ms__edfxtp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__einvn_1": _logic_module(
        "sky130_fd_sc_ms__einvn_1",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvn_2": _logic_module(
        "sky130_fd_sc_ms__einvn_2",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvn_4": _logic_module(
        "sky130_fd_sc_ms__einvn_4",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvn_8": _logic_module(
        "sky130_fd_sc_ms__einvn_8",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvp_1": _logic_module(
        "sky130_fd_sc_ms__einvp_1",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvp_2": _logic_module(
        "sky130_fd_sc_ms__einvp_2",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvp_4": _logic_module(
        "sky130_fd_sc_ms__einvp_4",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__einvp_8": _logic_module(
        "sky130_fd_sc_ms__einvp_8",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "sky130_fd_sc_ms__fa_1": _logic_module(
        "sky130_fd_sc_ms__fa_1",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fa_2": _logic_module(
        "sky130_fd_sc_ms__fa_2",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fa_4": _logic_module(
        "sky130_fd_sc_ms__fa_4",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fah_1": _logic_module(
        "sky130_fd_sc_ms__fah_1",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fah_2": _logic_module(
        "sky130_fd_sc_ms__fah_2",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fah_4": _logic_module(
        "sky130_fd_sc_ms__fah_4",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fahcin_1": _logic_module(
        "sky130_fd_sc_ms__fahcin_1",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__fahcon_1": _logic_module(
        "sky130_fd_sc_ms__fahcon_1",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT_N", "SUM"],
    ),
    "sky130_fd_sc_ms__fill_1": _logic_module(
        "sky130_fd_sc_ms__fill_1", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__fill_2": _logic_module(
        "sky130_fd_sc_ms__fill_2", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__fill_4": _logic_module(
        "sky130_fd_sc_ms__fill_4", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__fill_8": _logic_module(
        "sky130_fd_sc_ms__fill_8", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__fill_diode_2": _logic_module(
        "sky130_fd_sc_ms__fill_diode_2", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__fill_diode_4": _logic_module(
        "sky130_fd_sc_ms__fill_diode_4", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__fill_diode_8": _logic_module(
        "sky130_fd_sc_ms__fill_diode_8", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__ha_1": _logic_module(
        "sky130_fd_sc_ms__ha_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__ha_2": _logic_module(
        "sky130_fd_sc_ms__ha_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__ha_4": _logic_module(
        "sky130_fd_sc_ms__ha_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "sky130_fd_sc_ms__inv_1": _logic_module(
        "sky130_fd_sc_ms__inv_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__inv_2": _logic_module(
        "sky130_fd_sc_ms__inv_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__inv_4": _logic_module(
        "sky130_fd_sc_ms__inv_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__inv_8": _logic_module(
        "sky130_fd_sc_ms__inv_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__inv_16": _logic_module(
        "sky130_fd_sc_ms__inv_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__latchupcell": _logic_module(
        "sky130_fd_sc_ms__latchupcell", "Medium Speed", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_ms__maj3_1": _logic_module(
        "sky130_fd_sc_ms__maj3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__maj3_2": _logic_module(
        "sky130_fd_sc_ms__maj3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__maj3_4": _logic_module(
        "sky130_fd_sc_ms__maj3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__mux2_1": _logic_module(
        "sky130_fd_sc_ms__mux2_1",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__mux2_2": _logic_module(
        "sky130_fd_sc_ms__mux2_2",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__mux2_4": _logic_module(
        "sky130_fd_sc_ms__mux2_4",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__mux2i_1": _logic_module(
        "sky130_fd_sc_ms__mux2i_1",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__mux2i_2": _logic_module(
        "sky130_fd_sc_ms__mux2i_2",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__mux2i_4": _logic_module(
        "sky130_fd_sc_ms__mux2i_4",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__mux4_1": _logic_module(
        "sky130_fd_sc_ms__mux4_1",
        "Medium Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__mux4_2": _logic_module(
        "sky130_fd_sc_ms__mux4_2",
        "Medium Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__mux4_4": _logic_module(
        "sky130_fd_sc_ms__mux4_4",
        "Medium Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__nand2_1": _logic_module(
        "sky130_fd_sc_ms__nand2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand2_2": _logic_module(
        "sky130_fd_sc_ms__nand2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand2_4": _logic_module(
        "sky130_fd_sc_ms__nand2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand2_8": _logic_module(
        "sky130_fd_sc_ms__nand2_8",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand2b_1": _logic_module(
        "sky130_fd_sc_ms__nand2b_1",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand2b_2": _logic_module(
        "sky130_fd_sc_ms__nand2b_2",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand2b_4": _logic_module(
        "sky130_fd_sc_ms__nand2b_4",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand3_1": _logic_module(
        "sky130_fd_sc_ms__nand3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand3_2": _logic_module(
        "sky130_fd_sc_ms__nand3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand3_4": _logic_module(
        "sky130_fd_sc_ms__nand3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand3b_1": _logic_module(
        "sky130_fd_sc_ms__nand3b_1",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand3b_2": _logic_module(
        "sky130_fd_sc_ms__nand3b_2",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand3b_4": _logic_module(
        "sky130_fd_sc_ms__nand3b_4",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4_1": _logic_module(
        "sky130_fd_sc_ms__nand4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4_2": _logic_module(
        "sky130_fd_sc_ms__nand4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4_4": _logic_module(
        "sky130_fd_sc_ms__nand4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4b_1": _logic_module(
        "sky130_fd_sc_ms__nand4b_1",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4b_2": _logic_module(
        "sky130_fd_sc_ms__nand4b_2",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4b_4": _logic_module(
        "sky130_fd_sc_ms__nand4b_4",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4bb_1": _logic_module(
        "sky130_fd_sc_ms__nand4bb_1",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4bb_2": _logic_module(
        "sky130_fd_sc_ms__nand4bb_2",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nand4bb_4": _logic_module(
        "sky130_fd_sc_ms__nand4bb_4",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2_1": _logic_module(
        "sky130_fd_sc_ms__nor2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2_2": _logic_module(
        "sky130_fd_sc_ms__nor2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2_4": _logic_module(
        "sky130_fd_sc_ms__nor2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2_8": _logic_module(
        "sky130_fd_sc_ms__nor2_8",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2b_1": _logic_module(
        "sky130_fd_sc_ms__nor2b_1",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2b_2": _logic_module(
        "sky130_fd_sc_ms__nor2b_2",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor2b_4": _logic_module(
        "sky130_fd_sc_ms__nor2b_4",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor3_1": _logic_module(
        "sky130_fd_sc_ms__nor3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor3_2": _logic_module(
        "sky130_fd_sc_ms__nor3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor3_4": _logic_module(
        "sky130_fd_sc_ms__nor3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor3b_1": _logic_module(
        "sky130_fd_sc_ms__nor3b_1",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor3b_2": _logic_module(
        "sky130_fd_sc_ms__nor3b_2",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor3b_4": _logic_module(
        "sky130_fd_sc_ms__nor3b_4",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4_1": _logic_module(
        "sky130_fd_sc_ms__nor4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4_2": _logic_module(
        "sky130_fd_sc_ms__nor4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4_4": _logic_module(
        "sky130_fd_sc_ms__nor4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4b_1": _logic_module(
        "sky130_fd_sc_ms__nor4b_1",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4b_2": _logic_module(
        "sky130_fd_sc_ms__nor4b_2",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4b_4": _logic_module(
        "sky130_fd_sc_ms__nor4b_4",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4bb_1": _logic_module(
        "sky130_fd_sc_ms__nor4bb_1",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4bb_2": _logic_module(
        "sky130_fd_sc_ms__nor4bb_2",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__nor4bb_4": _logic_module(
        "sky130_fd_sc_ms__nor4bb_4",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o2bb2a_1": _logic_module(
        "sky130_fd_sc_ms__o2bb2a_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o2bb2a_2": _logic_module(
        "sky130_fd_sc_ms__o2bb2a_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o2bb2a_4": _logic_module(
        "sky130_fd_sc_ms__o2bb2a_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o2bb2ai_1": _logic_module(
        "sky130_fd_sc_ms__o2bb2ai_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o2bb2ai_2": _logic_module(
        "sky130_fd_sc_ms__o2bb2ai_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o2bb2ai_4": _logic_module(
        "sky130_fd_sc_ms__o2bb2ai_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o21a_1": _logic_module(
        "sky130_fd_sc_ms__o21a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o21a_2": _logic_module(
        "sky130_fd_sc_ms__o21a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o21a_4": _logic_module(
        "sky130_fd_sc_ms__o21a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o21ai_1": _logic_module(
        "sky130_fd_sc_ms__o21ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o21ai_2": _logic_module(
        "sky130_fd_sc_ms__o21ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o21ai_4": _logic_module(
        "sky130_fd_sc_ms__o21ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o21ba_1": _logic_module(
        "sky130_fd_sc_ms__o21ba_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o21ba_2": _logic_module(
        "sky130_fd_sc_ms__o21ba_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o21ba_4": _logic_module(
        "sky130_fd_sc_ms__o21ba_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o21bai_1": _logic_module(
        "sky130_fd_sc_ms__o21bai_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o21bai_2": _logic_module(
        "sky130_fd_sc_ms__o21bai_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o21bai_4": _logic_module(
        "sky130_fd_sc_ms__o21bai_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o22a_1": _logic_module(
        "sky130_fd_sc_ms__o22a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o22a_2": _logic_module(
        "sky130_fd_sc_ms__o22a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o22a_4": _logic_module(
        "sky130_fd_sc_ms__o22a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o22ai_1": _logic_module(
        "sky130_fd_sc_ms__o22ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o22ai_2": _logic_module(
        "sky130_fd_sc_ms__o22ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o22ai_4": _logic_module(
        "sky130_fd_sc_ms__o22ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o31a_1": _logic_module(
        "sky130_fd_sc_ms__o31a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o31a_2": _logic_module(
        "sky130_fd_sc_ms__o31a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o31a_4": _logic_module(
        "sky130_fd_sc_ms__o31a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o31ai_1": _logic_module(
        "sky130_fd_sc_ms__o31ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o31ai_2": _logic_module(
        "sky130_fd_sc_ms__o31ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o31ai_4": _logic_module(
        "sky130_fd_sc_ms__o31ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o32a_1": _logic_module(
        "sky130_fd_sc_ms__o32a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o32a_2": _logic_module(
        "sky130_fd_sc_ms__o32a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o32a_4": _logic_module(
        "sky130_fd_sc_ms__o32a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o32ai_1": _logic_module(
        "sky130_fd_sc_ms__o32ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o32ai_2": _logic_module(
        "sky130_fd_sc_ms__o32ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o32ai_4": _logic_module(
        "sky130_fd_sc_ms__o32ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o41a_1": _logic_module(
        "sky130_fd_sc_ms__o41a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o41a_2": _logic_module(
        "sky130_fd_sc_ms__o41a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o41a_4": _logic_module(
        "sky130_fd_sc_ms__o41a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o41ai_1": _logic_module(
        "sky130_fd_sc_ms__o41ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o41ai_2": _logic_module(
        "sky130_fd_sc_ms__o41ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o41ai_4": _logic_module(
        "sky130_fd_sc_ms__o41ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o211a_1": _logic_module(
        "sky130_fd_sc_ms__o211a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o211a_2": _logic_module(
        "sky130_fd_sc_ms__o211a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o211a_4": _logic_module(
        "sky130_fd_sc_ms__o211a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o211ai_1": _logic_module(
        "sky130_fd_sc_ms__o211ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o211ai_2": _logic_module(
        "sky130_fd_sc_ms__o211ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o211ai_4": _logic_module(
        "sky130_fd_sc_ms__o211ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o221a_1": _logic_module(
        "sky130_fd_sc_ms__o221a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o221a_2": _logic_module(
        "sky130_fd_sc_ms__o221a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o221a_4": _logic_module(
        "sky130_fd_sc_ms__o221a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o221ai_1": _logic_module(
        "sky130_fd_sc_ms__o221ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o221ai_2": _logic_module(
        "sky130_fd_sc_ms__o221ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o221ai_4": _logic_module(
        "sky130_fd_sc_ms__o221ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o311a_1": _logic_module(
        "sky130_fd_sc_ms__o311a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o311a_2": _logic_module(
        "sky130_fd_sc_ms__o311a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o311a_4": _logic_module(
        "sky130_fd_sc_ms__o311a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o311ai_1": _logic_module(
        "sky130_fd_sc_ms__o311ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o311ai_2": _logic_module(
        "sky130_fd_sc_ms__o311ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o311ai_4": _logic_module(
        "sky130_fd_sc_ms__o311ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o2111a_1": _logic_module(
        "sky130_fd_sc_ms__o2111a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o2111a_2": _logic_module(
        "sky130_fd_sc_ms__o2111a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o2111a_4": _logic_module(
        "sky130_fd_sc_ms__o2111a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__o2111ai_1": _logic_module(
        "sky130_fd_sc_ms__o2111ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o2111ai_2": _logic_module(
        "sky130_fd_sc_ms__o2111ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__o2111ai_4": _logic_module(
        "sky130_fd_sc_ms__o2111ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__or2_1": _logic_module(
        "sky130_fd_sc_ms__or2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or2_2": _logic_module(
        "sky130_fd_sc_ms__or2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or2_4": _logic_module(
        "sky130_fd_sc_ms__or2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or2b_1": _logic_module(
        "sky130_fd_sc_ms__or2b_1",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or2b_2": _logic_module(
        "sky130_fd_sc_ms__or2b_2",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or2b_4": _logic_module(
        "sky130_fd_sc_ms__or2b_4",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or3_1": _logic_module(
        "sky130_fd_sc_ms__or3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or3_2": _logic_module(
        "sky130_fd_sc_ms__or3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or3_4": _logic_module(
        "sky130_fd_sc_ms__or3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or3b_1": _logic_module(
        "sky130_fd_sc_ms__or3b_1",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or3b_2": _logic_module(
        "sky130_fd_sc_ms__or3b_2",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or3b_4": _logic_module(
        "sky130_fd_sc_ms__or3b_4",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4_1": _logic_module(
        "sky130_fd_sc_ms__or4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4_2": _logic_module(
        "sky130_fd_sc_ms__or4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4_4": _logic_module(
        "sky130_fd_sc_ms__or4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4b_1": _logic_module(
        "sky130_fd_sc_ms__or4b_1",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4b_2": _logic_module(
        "sky130_fd_sc_ms__or4b_2",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4b_4": _logic_module(
        "sky130_fd_sc_ms__or4b_4",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4bb_1": _logic_module(
        "sky130_fd_sc_ms__or4bb_1",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4bb_2": _logic_module(
        "sky130_fd_sc_ms__or4bb_2",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__or4bb_4": _logic_module(
        "sky130_fd_sc_ms__or4bb_4",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__sdfbbn_1": _logic_module(
        "sky130_fd_sc_ms__sdfbbn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_ms__sdfbbn_2": _logic_module(
        "sky130_fd_sc_ms__sdfbbn_2",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sky130_fd_sc_ms__sdfbbp_1": _logic_module(
        "sky130_fd_sc_ms__sdfbbp_1",
        "Medium Speed",
        [
            "CLK",
            "D",
            "RESET_B",
            "SCD",
            "SCE",
            "SET_B",
            "VGND",
            "VNB",
            "VPB",
            "VPWR",
            "Q",
        ],
    ),
    "sky130_fd_sc_ms__sdfrbp_1": _logic_module(
        "sky130_fd_sc_ms__sdfrbp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sdfrbp_2": _logic_module(
        "sky130_fd_sc_ms__sdfrbp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sdfrtn_1": _logic_module(
        "sky130_fd_sc_ms__sdfrtn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfrtp_1": _logic_module(
        "sky130_fd_sc_ms__sdfrtp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfrtp_2": _logic_module(
        "sky130_fd_sc_ms__sdfrtp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfrtp_4": _logic_module(
        "sky130_fd_sc_ms__sdfrtp_4",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfsbp_1": _logic_module(
        "sky130_fd_sc_ms__sdfsbp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sdfsbp_2": _logic_module(
        "sky130_fd_sc_ms__sdfsbp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sdfstp_1": _logic_module(
        "sky130_fd_sc_ms__sdfstp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfstp_2": _logic_module(
        "sky130_fd_sc_ms__sdfstp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfstp_4": _logic_module(
        "sky130_fd_sc_ms__sdfstp_4",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfxbp_1": _logic_module(
        "sky130_fd_sc_ms__sdfxbp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sdfxbp_2": _logic_module(
        "sky130_fd_sc_ms__sdfxbp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sdfxtp_1": _logic_module(
        "sky130_fd_sc_ms__sdfxtp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfxtp_2": _logic_module(
        "sky130_fd_sc_ms__sdfxtp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdfxtp_4": _logic_module(
        "sky130_fd_sc_ms__sdfxtp_4",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sdlclkp_1": _logic_module(
        "sky130_fd_sc_ms__sdlclkp_1",
        "Medium Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ms__sdlclkp_2": _logic_module(
        "sky130_fd_sc_ms__sdlclkp_2",
        "Medium Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ms__sdlclkp_4": _logic_module(
        "sky130_fd_sc_ms__sdlclkp_4",
        "Medium Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sky130_fd_sc_ms__sedfxbp_1": _logic_module(
        "sky130_fd_sc_ms__sedfxbp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sedfxbp_2": _logic_module(
        "sky130_fd_sc_ms__sedfxbp_2",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sky130_fd_sc_ms__sedfxtp_1": _logic_module(
        "sky130_fd_sc_ms__sedfxtp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sedfxtp_2": _logic_module(
        "sky130_fd_sc_ms__sedfxtp_2",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__sedfxtp_4": _logic_module(
        "sky130_fd_sc_ms__sedfxtp_4",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sky130_fd_sc_ms__tap_1": _logic_module(
        "sky130_fd_sc_ms__tap_1", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__tap_2": _logic_module(
        "sky130_fd_sc_ms__tap_2", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__tapmet1_2": _logic_module(
        "sky130_fd_sc_ms__tapmet1_2", "Medium Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__tapvgnd2_1": _logic_module(
        "sky130_fd_sc_ms__tapvgnd2_1", "Medium Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__tapvgnd_1": _logic_module(
        "sky130_fd_sc_ms__tapvgnd_1", "Medium Speed", ["VGND", "VPB", "VPWR"]
    ),
    "sky130_fd_sc_ms__tapvpwrvgnd_1": _logic_module(
        "sky130_fd_sc_ms__tapvpwrvgnd_1", "Medium Speed", ["VGND", "VPWR"]
    ),
    "sky130_fd_sc_ms__xnor2_1": _logic_module(
        "sky130_fd_sc_ms__xnor2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__xnor2_2": _logic_module(
        "sky130_fd_sc_ms__xnor2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__xnor2_4": _logic_module(
        "sky130_fd_sc_ms__xnor2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "sky130_fd_sc_ms__xnor3_1": _logic_module(
        "sky130_fd_sc_ms__xnor3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xnor3_2": _logic_module(
        "sky130_fd_sc_ms__xnor3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xnor3_4": _logic_module(
        "sky130_fd_sc_ms__xnor3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xor2_1": _logic_module(
        "sky130_fd_sc_ms__xor2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xor2_2": _logic_module(
        "sky130_fd_sc_ms__xor2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xor2_4": _logic_module(
        "sky130_fd_sc_ms__xor2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xor3_1": _logic_module(
        "sky130_fd_sc_ms__xor3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xor3_2": _logic_module(
        "sky130_fd_sc_ms__xor3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sky130_fd_sc_ms__xor3_4": _logic_module(
        "sky130_fd_sc_ms__xor3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
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
for name, mod in hd.items():
    setattr(modules, name, mod)
for name, mod in hdll.items():
    setattr(modules, name, mod)
for name, mod in hs.items():
    setattr(modules, name, mod)
for name, mod in hvl.items():
    setattr(modules, name, mod)
for name, mod in lp.items():
    setattr(modules, name, mod)
for name, mod in ls.items():
    setattr(modules, name, mod)
for name, mod in ms.items():
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
