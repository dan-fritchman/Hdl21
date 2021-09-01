import hdl21 as h
import copy

from enum import Enum, auto
from typing import Callable, Union, Any, Optional, Dict, List
from pydantic.dataclasses import dataclass
from pydantic import ValidationError

# FIXME: is this built-in somewhere? Probably
Number = Union[int, float]


@dataclass
class Sim:
    dut: h.Module
    attrs: List["SpiceAttr"]


@dataclass
class Dc:
    var: str  # FIXME: more elaborate options here
    sweep: "Sweep"
    name: Optional[str] = None


@dataclass
class Ac:
    sweep: "Sweep"
    name: Optional[str] = None


@dataclass
class Tran:
    tstop: float
    name: Optional[str] = None


@dataclass
class SweepAnalysis:
    """Sweep an `inner` analysis."""

    inner: "Analysis"
    sweep: "Sweep"
    name: Optional[str] = None


@dataclass
class MonteCarlo:
    """Add monte-carlo variations to one or more `inner` analyses."""

    inner: List["Analysis"]
    npts: int
    name: Optional[str] = None


@dataclass
class CustomAnalysis:
    """String-defined, non-first-class analysis statement
    Primarily for simulator-specific specialty analyses."""

    cmd: str
    name: Optional[str] = None


# Analysis type-union
Analysis = Union[Dc, Ac, Tran, CustomAnalysis, MonteCarlo]


@dataclass
class LinearSweep:
    start: Number
    stop: Number
    step: Number


@dataclass
class LogSweep:
    start: int
    stop: int
    npts: int


@dataclass
class PointSweep:
    points: List[Number]


# Sweep type-union
Sweep = Union[LinearSweep, LogSweep, PointSweep]


class SaveMode(Enum):
    NONE = auto()
    ALL = auto()
    SELECTED = auto()


@dataclass
class Save:
    targ: Union[str, List[str], h.Signal, List[h.Signal], SaveMode]


@dataclass
class Meas:
    analysis: "Analysis"
    expr: str  # FIXME: just a string to be evaluated, no in-Python semantics


# Spice-Sim Attribute-Union
SpiceAttr = Union[Analysis, Save, Meas]

# Update all the forward-defined class-references
for cls in [Ac, Dc, Tran, Save, Meas, LinearSweep, LogSweep, PointSweep, Sim]:
    cls.__pydantic_model__.update_forward_refs()
