"""
Spice-Class Simulation Interface 
"""

from enum import Enum
from typing import Union, Any, Optional, List, get_args
from pathlib import Path
from dataclasses import field

# Local Imports
from ..datatype import datatype
from ..units import Prefixed
from ..module import Module
from ..signal import Signal, Port


# Union of numeric types, including the internally-defined `Prefixed`
Number = Union[int, float, Prefixed]


def is_number(val: Any) -> bool:
    return isinstance(val, get_args(Number))


def tb(name: str) -> Module:
    """ Create a new testbench module. 
    Includes the "testbench interface": 
    a single, scalar, undirected Port named "VSS". """
    tb = Module(name=name)
    tb.VSS = Port(width=1)
    return tb


def is_tb(m: Module) -> bool:
    """ Boolean indication of whether Module `m` meets the test-bench interface. """
    if len(m.ports) != 1:
        return False
    # There's exactly one port. Retrieve it from the `ports` dict,
    # first requiring getting its name from the `keys`.
    port = m.ports[list(m.ports.keys())[0]]
    return port.width == 1


_simattrs = {}


def simattr(cls) -> type:
    """ Add a class to the `simattrs` set of generation methods. 
    This is the magic that enables methods including: 
    ```python 
    sim = Sim()
    sim.param(**kwargs)
    sim.dc(**kwargs)
    sim.tran(**kwargs)
    ```
    To create the classes defined here, and add them to `sim`. 
    """

    # Class names are lower-cases to create the dictionary key,
    # which also becomes the method-name on `sim`
    _simattrs[cls.__name__.lower()] = cls
    return cls


@simattr
@datatype
class Param:
    """ Simulation Parameter-Value """

    name: str  # Parameter Name
    val: Any  # Parameter Value


@datatype
class LinearSweep:
    """ Linear Sweep """

    start: Number
    stop: Number
    step: Number


@datatype
class LogSweep:
    """ Logarithmic / Decade Sweep """

    start: float
    stop: float
    npts: int


@datatype
class PointSweep:
    """ List of Points Sweep """

    points: List[Number]


# Sweep type-union
Sweep = Union[LinearSweep, LogSweep, PointSweep]


def is_sweep(val: Any) -> bool:
    return isinstance(val, get_args(Sweep))


@simattr
@datatype
class Dc:
    """ DC Steady-State Analysis """

    var: Union[str, Param]  # Swept parameter, or its name
    sweep: Sweep  # Sweep values
    name: Optional[str] = None  # Optional analysis name


@simattr
@datatype
class Ac:
    """ AC Small-Signal Analysis """

    sweep: LogSweep  # Sweep values. Always log-valued.
    name: Optional[str] = None  # Optional analysis name


@simattr
@datatype
class Tran:
    """ Transient Analysis """

    tstop: Number  # Stop time
    tstep: Optional[Number] = None  # Optional time-step recommendation
    name: Optional[str] = None  # Optional analysis name


@simattr
@datatype
class SweepAnalysis:
    """ Sweep over `inner` analyses """

    inner: List["Analysis"]  # Inner Analyses
    var: Union[str, Param]  # Sweep variable, or its name
    sweep: Sweep  # Sweep Values
    name: Optional[str] = None  # Optional analysis name


@simattr
@datatype
class MonteCarlo:
    """ Add monte-carlo variations to one or more `inner` analyses. """

    inner: List["Analysis"]  # Inner Analyses
    npts: int  # Number of points
    name: Optional[str] = None  # Optional analysis name


@simattr
@datatype
class CustomAnalysis:
    """ String-defined, non-first-class analysis statement
    Primarily for simulator-specific specialty analyses. """

    cmd: str  # Analysis command string
    name: Optional[str] = None  #


# Analysis type-union
Analysis = Union[Dc, Ac, Tran, SweepAnalysis, MonteCarlo, CustomAnalysis]


def is_analysis(val: Any) -> bool:
    return isinstance(val, get_args(Analysis))


class SaveMode(Enum):
    """ Enumerated data-saving modes """

    NONE = "none"
    ALL = "all"
    SELECTED = "selected"


# Union of "save-able" types
SaveTarget = Union[
    SaveMode,  # A `SaveMode`, e.g. `SaveMode.ALL`
    Signal,  # A single `Signal`
    List[Signal],  # A list of `Signal`s
    str,  # A signal signale-name
    List[str],  # A list of signal-names
]


@simattr
@datatype
class Save:
    """ Save Control-Element 
    Adds content to the target simulation output """

    targ: SaveTarget


@simattr
@datatype
class Meas:
    """ Measurement """

    analysis: Union["Analysis", str]  # Target `Analysis`, or its name
    name: str  # Measurement name
    expr: str  # Measured expression. FIXME: just a string to be evaluated, no in-Python semantics


@simattr
@datatype
class Include:
    """ Include a File Path """

    path: Path


@simattr
@datatype
class Lib:
    """ Include a Library Section """

    path: Path
    section: str


@simattr
@datatype
class Literal:
    """ Simulation-Control Literal, 
    expressed as netlist-language text for a particular target language. """

    txt: str


# Spice-Sim Attribute-Union
Control = Union[Include, Lib, Save, Meas, Param, Literal]


def is_control(val: Any) -> bool:
    return isinstance(val, get_args(Control))


@simattr
@datatype
class Options:
    """ Simulation Options """

    temper: Optional[int] = None  # Temperature
    tnom: Optional[int] = None  # Nominal temperature
    gmin: Optional[float] = None
    reltol: Optional[float] = None
    iabstol: Optional[float] = None


# Spice-Sim Attribute-Union
SimAttr = Union[Analysis, Control, Options]


def is_simattr(val: Any) -> bool:
    return isinstance(val, get_args(SimAttr))


@datatype
class Sim:
    """ 
    # Simulation Input 

    Comprises a `Module` DUT and set of simulation control input. 
    DUT Modules must adhere to the testbench IO interface: 
    A single, width-one port, nominally named "VSS", 
    and expected to be connected from "simulator ground" to the Module's ground. 
    """

    # Testbench `Module`, with its dependencies via `Instance`s
    dut: Module
    # Simulation Control Attributes
    attrs: List[SimAttr] = field(default_factory=list)

    def add(self, *attrs: List[SimAttr]) -> Union[SimAttr, List[SimAttr]]:
        """ Add one or more `SimAttr`s to the simulation. 
        Returns the inserted attributes, either as a list or a single `SimAttr`. """
        for attr in attrs:
            self.attrs.append(attr)
        if len(attrs) == 1:
            return attrs[0]
        return list(attrs)


def _add_attr_func(name: str, cls: type):
    # Create the internal "construct + add" closure
    def _method(self, *args, **kwargs):
        inst = cls(*args, **kwargs)
        self.add(inst)
        return inst

    # Set its name to the `simattr` name
    _method.__name__ = name
    # And set it as a method on `Sim`
    setattr(Sim, name, _method)


# Add all the `simattrs` as methods on `Sim`
for name, cls in _simattrs.items():
    _add_attr_func(name, cls)

