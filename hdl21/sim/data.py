"""
Spice-Class Simulation Interface 
"""

from decimal import Decimal
from enum import Enum
from typing import Union, Any, Optional, List, Sequence, Awaitable
from pathlib import Path
from dataclasses import field

import vlsirtools.spice as vsp

# Create a few aliases to the VLSIR sim-results types
from vlsirtools.spice import SimResultUnion
from vlsirtools.spice.sim_data import SimResult
from vlsir.spice_pb2 import SimResult as SimResultProto

# Local Imports
from ..one_or_more import OneOrMore
from ..datatype import datatype
from ..instance import Instance
from ..signal import Signal, Port
from ..instantiable import Instantiable, Module, GeneratorCall, ExternalModuleCall
from ..scalar import Scalar
from ..literal import Literal

# FIXME: deprecate `ParamVal`.
# Users may be importing it as `ParamVal` from here, so leave this name for now.
ParamVal = Scalar


def tb(name: str) -> Module:
    """Create a new testbench module.
    Includes the "testbench interface":
    a single, scalar, undirected Port named "VSS"."""
    tb = Module(name=name)
    tb.VSS = Port(width=1)
    return tb


def is_tb(i: Instantiable) -> bool:
    """Boolean indication of whether Module `m` meets the test-bench interface."""
    if isinstance(i, (Module, ExternalModuleCall)):
        m = i
    elif isinstance(i, GeneratorCall):
        m = i.result
    else:
        raise TypeError(f"Invalid un-instantiable argument {i} to `is_tb`")

    if len(m.ports) != 1:
        return False

    # There's exactly one port. Retrieve it from the `ports` dict,
    # first requiring getting its name from the `keys`.
    port = m.ports[list(m.ports.keys())[0]]

    # While that port is *conventionally* called "VSS", it *can* be called anything.
    # The testbench interface is met so long as we have a single, scalar port.
    return port.width == 1


_simattrs = {}


def simattr(cls) -> type:
    """
    Add a class to the `simattrs` set of generation methods.
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
    # which also becomes the method-name on `sim`.
    _simattrs[cls.__name__.lower()] = cls
    return cls


# Apply that "decorator" to the `Literal` class
simattr(Literal)


@simattr
@datatype
class Param:
    """Simulation Parameter-Value"""

    # Parameter Value
    val: Scalar
    # Parameter Name. Generally required at simulation-time, but `Optional` for during construction stages.
    name: Optional[str] = None


@datatype
class LinearSweep:
    """Linear Sweep"""

    start: Scalar
    stop: Scalar
    step: Scalar


@datatype
class LogSweep:
    """Logarithmic / Decade Sweep"""

    start: Scalar
    stop: Scalar
    npts: int


@datatype
class PointSweep:
    """List of Points Sweep"""

    points: List[Scalar]


# Sweep type-union
Sweep = Union[LinearSweep, LogSweep, PointSweep]


def is_sweep(val: Any) -> bool:
    return isinstance(val, Sweep.__args__)


class AnalysisType(Enum):
    """Enumerated Analysis-Types
    Corresponding to the entries in the `Analysis` type-union."""

    OP = "op"
    DC = "dc"
    AC = "ac"
    TRAN = "tran"
    NOISE = "noise"
    MONTE = "monte"
    SWEEP = "sweep"
    CUSTOM = "custom"


@simattr
@datatype
class Op:
    """Operating Point Analysis"""

    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.OP


@simattr
@datatype
class Dc:
    """DC Steady-State Analysis"""

    var: Union[str, Param]  # Swept parameter, or its name
    sweep: Sweep  # Sweep values
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.DC


@simattr
@datatype
class Ac:
    """AC Small-Signal Analysis"""

    sweep: LogSweep  # Frequency sweep values. Always log-valued.
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.AC


@simattr
@datatype
class Tran:
    """Transient Analysis"""

    tstop: Scalar  # Stop time
    tstep: Optional[Scalar] = None  # Optional time-step recommendation
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.TRAN


@simattr
@datatype
class Noise:
    """Noise Analysis"""

    # Output, either as a signal or pair thereof
    # NOTE: the type of `output` is really `Union[Connectable, Tuple[Connectable, Connectable]]`
    # we can't quite check this statically, but do check when serializing.
    output: Any

    # Input voltage or current source
    input_source: Union[Instance, str]

    sweep: LogSweep  # Frequency sweep values. Always log-valued.
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.NOISE


@simattr
@datatype
class SweepAnalysis:
    """Sweep over `inner` analyses"""

    inner: List["Analysis"]  # Inner Analyses
    var: Union[str, Param]  # Sweep variable, or its name
    sweep: Sweep  # Sweep Values
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.SWEEP


@simattr
@datatype
class MonteCarlo:
    """Add monte-carlo variations to one or more `inner` analyses."""

    inner: List["Analysis"]  # Inner Analyses
    npts: int  # Number of points
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.MONTE


@simattr
@datatype
class CustomAnalysis:
    """String-defined, non-first-class analysis statement
    Primarily for simulator-specific specialty analyses."""

    cmd: str  # Analysis command string
    name: Optional[str] = None  # Optional analysis name

    @property
    def tp(self) -> AnalysisType:
        return AnalysisType.CUSTOM


# Analysis type-union
Analysis = Union[Op, Dc, Ac, Tran, Noise, SweepAnalysis, MonteCarlo, CustomAnalysis]


def is_analysis(val: Any) -> bool:
    return isinstance(val, Analysis.__args__)


class SaveMode(Enum):
    """Enumerated data-saving modes"""

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
    """Save Control-Element
    Adds content to the target simulation output"""

    targ: SaveTarget


@simattr
@datatype
class Meas:
    """Measurement"""

    analysis: Union["Analysis", str]  # Target `Analysis`, or its type-name
    expr: str  # Measured expression. FIXME: just a string to be evaluated, no in-Python semantics
    name: Optional[str] = None  # Measurement name


@simattr
@datatype
class Include:
    """Include a File Path"""

    path: Path  # Path to include
    name: Optional[str] = None  # Name, used in class-based `Sim` definitions


@simattr
@datatype
class Lib:
    """Include a Library Section"""

    path: Path  # Path to include
    section: str  # Library Section
    name: Optional[str] = None  # Name, used in class-based `Sim` definitions


# Spice-Sim Attribute-Union
Control = Union[Include, Lib, Save, Meas, Param, Literal]


def is_control(val: Any) -> bool:
    return isinstance(val, Control.__args__)


@simattr
@datatype
class Options:
    """Simulation Options"""

    temper: Optional[int] = None  # Temperature
    tnom: Optional[int] = None  # Nominal temperature
    # FIXME NOTE: these three will in short order become `Scalar`s!
    gmin: Optional[float] = None
    reltol: Optional[float] = None
    iabstol: Optional[float] = None

    name: Optional[str] = None  # Name, used in class-based `Sim` definitions


# Spice-Sim Attribute-Union
SimAttr = Union[Analysis, Control, Options]


def is_simattr(val: Any) -> bool:
    return isinstance(val, SimAttr.__args__)


@datatype
class Sim:
    """
    # Simulation Input

    Comprises a `Instantiable`, typically `Module`, testbench and set of simulation control input.
    Testbenches must adhere to the testbench IO interface:
    A single, width-one port, nominally named "VSS", and expected to be connected from "simulator ground" to the DUT's ground.
    """

    # Testbench, with its dependencies via `Instance`s
    tb: Instantiable
    # Simulation Control Attributes
    attrs: List[SimAttr] = field(default_factory=list)
    # Optional simulation name
    name: Optional[str] = None

    def add(self, *attrs: List[SimAttr]) -> OneOrMore[SimAttr]:
        """Add one or more `SimAttr`s to the simulation.
        Returns the inserted attributes, either as a list or a single `SimAttr`."""
        for attr in attrs:
            if not is_simattr(attr):
                raise TypeError
            self.attrs.append(attr)
        if len(attrs) == 1:
            return attrs[0]
        return list(attrs)

    def run(self, opts: Optional[vsp.SimOptions] = None) -> vsp.SimResultUnion:
        """Invoke simulation via `vlsirtools.spice`."""
        return run(self, opts=opts)

    async def run_async(
        self, opts: Optional[vsp.SimOptions] = None
    ) -> Awaitable[vsp.SimResultUnion]:
        """Invoke simulation via `vlsirtools.spice`."""
        return run_async(self, opts=opts)


def run(
    inp: OneOrMore[Sim], opts: Optional[vsp.SimOptions] = None
) -> OneOrMore[vsp.SimResultUnion]:
    """Invoke one or more `Sim`s via `vlsirtools.spice`."""

    from .to_proto import to_proto

    return vsp.sim(inp=to_proto(inp), opts=opts)


async def run_async(
    inp: OneOrMore[Sim], opts: Optional[vsp.SimOptions] = None
) -> OneOrMore[Awaitable[vsp.SimResultUnion]]:
    """Invoke simulation via `vlsirtools.spice`."""
    from .to_proto import to_proto

    return await vsp.sim_async(inp=to_proto(inp), opts=opts)


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


def sim(cls: type) -> Sim:
    """
    # `Sim` Definition Decorator

    Converts a class-body full of simulation attributes (`SimAttr`s) to a `Sim`.
    Example Usage:

    ```python
    import hdl21 as h
    from hdl21.sim import *

    @sim
    class MySim:
        tb = tb(name="mytb")

        x = Param(5)
        y = Param(6)
        mydc = Dc(var=x, sweep=PointSweep([1]))
        myac = Ac(sweep=LogSweep(1e1, 1e10, 10))
        mytran = Tran(tstop=11 * h.prefix.PICO)
        mysweep = SweepAnalysis(
            inner=[mytran],
            var=x,
            sweep=LinearSweep(0, 1, 2),
        )
        mymc = MonteCarlo(
            inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc")],
            npts=11,
        )
        delay = Meas(analysis=mytran, expr="trig_targ_something")
        opts = Options(reltol=1e-9)

        # Attributes whose names don't really matter can be called anything,
        # but must be *assigned* into the class, not just constructed.
        save_all = Save(SaveMode.ALL)

        # Non-`SimAttr`s such as `a_path` below will be dropped from the `Sim` definition,
        # but can be referred to by the following attributes.
        a_path = "/home/models"
        include_that_path = Include(a_path)
        fast_lib = Lib(path=a_path, section="fast")
    ```

    Class-based `Sim` definitions retain all class members which are `SimAttr`s and drop all others.
    Non-`SimAttr`-valued fields can nonetheless be handy for defining intermediate values upon which the ultimate SimAttrs depend,
    such as the `a_path` field in the example aboe.

    Classes decoratated by `sim` a single special required field:
    a `tb` attribute which sets the simulation testbench.

    Several other names are disallowed in `sim` class-definitions,
    generally corresponding to the names of the `Sim` class's fields and methods.
    Disallowed names include: `["attrs", "add", "run", "namespace"]`.
    """

    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.sim inheriting from {cls.__bases__}")

    protected_names = ["attrs", "add", "run", "namespace"]

    # Initialize the content of the eventual `Sim`.
    # Note we largely can't create it now because the `tb` field is required at construction time.
    name: Optional[str] = None
    tb: Optional[Instantiable] = None
    attrs: List[SimAttr] = list()

    # Any class-body content that isn't either (a) one of those special names, or (b) a `SimAttr`,
    # will be "forgotten" from the `Sim` definition.
    # This can nonetheless be handy for defining intermediate values upon which the ultimate SimAttrs depend.
    forgetme: List[Any] = list()

    # Take a lap through the class dictionary, type-check everything and assign relevant attributes to the sim
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in Sim {cls}")
        elif key == "tb":  # Set the test-bench attribute
            tb = val
        elif key == "name":  # Set the sim-name attribute
            name = val
        elif is_simattr(val):
            # Add to the sim-attributes list
            # Special case Python's conventional "ignored" name, the underscore.
            # Leave attributes named "_"'s `name` field set to `None`.
            if key != "_":
                val.name = key
            attrs.append(val)
        else:  # Add to the forget-list
            forgetme.append(val)

    if tb is None:
        raise RuntimeError(f"No `tb` defined in Sim {cls}")

    # Create the `Sim` object
    name = name or cls.__name__
    sim = Sim(name=name, tb=tb, attrs=attrs)

    # And return the `Sim`
    return sim
