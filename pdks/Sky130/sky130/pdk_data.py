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
        dtype=h.Scalar,
        desc="Drain Area",
        default=h.Literal("int((nf+1)/2) * w/nf * 0.29"),
    )

    # This unfortunate naming is to prevent conflicts with base python.
    As = h.Param(
        dtype=h.Scalar,
        desc="Source Area",
        default=h.Literal("int((nf+2)/2) * w/nf * 0.29"),
    )

    pd = h.Param(
        dtype=h.Scalar,
        desc="Drain Perimeter",
        default=h.Literal("2*int((nf+1)/2) * (w/nf + 0.29)"),
    )
    ps = h.Param(
        dtype=h.Scalar,
        desc="Source Perimeter",
        default=h.Literal("2*int((nf+2)/2) * (w/nf + 0.29)"),
    )
    nrd = h.Param(
        dtype=h.Scalar, desc="Drain Resistive Value", default=h.Literal("0.29 / w")
    )
    nrs = h.Param(
        dtype=h.Scalar, desc="Source Resistive Value", default=h.Literal("0.29 / w")
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


def xtor_module(
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


def res_module(
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


def diode_module(
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


def bjt_module(
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


def cap_module(
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


def vpp_module(
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


def logic_module(
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
