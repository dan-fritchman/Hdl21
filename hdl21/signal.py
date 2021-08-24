"""
# hdl21 Signals and Ports 

Signals are Hdl21's base-level unit of hardware connectivity. 

Each `Signal` is analogous in content to a *bus* or (single-dimensional) *array* in many legacy HDLs. 
(Most similar to Verilog's packed single-dimensional arrays.) 
The `Signal.width` field indicates the bit-width of said bus. 
It defaults to one for scalar Signals. 
Widths of zero or less generate errors, both at construction-time and later. 

Hdl21 `Signals` are *untyped*. 
They represent a connection, not the type or value of data it carries. 
In this sense they are more similar to analog-style environments than to most legacy HDLs. 

`Ports`, `Inputs`, `Outputs`, and `Inouts` are not dedicated Hdl21 types, 
but thin convenience function-wrappers around `Signal`. 
Each `Signal` includes enumerated fields for its visibility (internal vs port) 
and direction. For internal `Signals`, the `direction` field is globally expected to be ignored. 

"""

from typing import Optional, Any, List, Union
from enum import Enum
from dataclasses import field
from pydantic.dataclasses import dataclass

# Local imports
from .connect import connectable


class PortDir(Enum):
    """ Port-Direction Enumeration """

    INPUT = 0
    OUTPUT = 1
    INOUT = 2
    NONE = 3


class Visibility(Enum):
    """ Port-Visibility Enumeration """

    INTERNAL = 0
    PORT = 1


@connectable
@dataclass
class Signal:
    """
    # hdl21 Signal
    The base-level unit of hardware connectivity
    """

    name: Optional[str] = None
    width: int = 1
    vis: Visibility = Visibility.INTERNAL
    direction: PortDir = PortDir.NONE
    desc: Optional[str] = None  # Description
    src: Optional[Enum] = field(repr=False, default=None)
    dest: Optional[Enum] = field(repr=False, default=None)

    def __post_init_post_parse__(self):
        if self.width < 1:
            raise ValueError

    def __getitem__(self, key: Any) -> "Slice":
        """ Square-Bracket Slicing into Signals, returning Signal-Slices.
        Does *HDL-style* slicing, in which:
        * Slice indices are *inclusive*
        * Larger arguments are expected to come *first*.

        e.g. The top "half" of a width-ten `Signal` can be retrieved via:
        `Signal(width=10)[9:5]` """

        if isinstance(key, int):
            if key >= self.width:
                raise ValueError(f"Out-of-bounds index {key} into {self}")
            if key < 0:
                raise ValueError(f"Invalid negative index {key} into {self}")
            return Slice(signal=self, top=key, bot=key)

        if isinstance(key, slice):
            # Note these `slice` attributes are descriptor-things, and they get weird, fast.
            # Extracting their three key fields the most-hardest way via `__getattribute__` seems to work cleanest.
            start = slice.__getattribute__(key, "start")
            stop = slice.__getattribute__(key, "stop")
            step = slice.__getattribute__(key, "step")
            if step is not None:
                raise ValueError(f"Invalid slice (with step) {key} indexed into {self}")
            top = start or self.width - 1
            if top > self.width:
                raise ValueError(f"Out-of-bounds index {top} into {self}")
            if top < 0:
                raise ValueError(f"Invalid negative index {top} into {self}")
            bot = stop or 0
            if bot > self.width:
                raise ValueError(f"Out-of-bounds index {bot} into {self}")
            if bot < 0:
                raise ValueError(f"Invalid negative index {bot} into {self}")
            if bot >= top:
                raise ValueError(f"Invalid slice (start <= stop) {key} into {self}")
            return Slice(signal=self, top=top, bot=bot)

        raise TypeError(f"Invalid slice-type {key} into {self}")


def Input(**kwargs) -> Signal:
    """ Input Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(vis=Visibility.PORT, direction=PortDir.INPUT, **kwargs)


def Output(**kwargs) -> Signal:
    """ Output Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(vis=Visibility.PORT, direction=PortDir.OUTPUT, **kwargs)


def Inout(**kwargs) -> Signal:
    """ Inout Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(vis=Visibility.PORT, direction=PortDir.INOUT, **kwargs)


def Port(direction=PortDir.NONE, **kwargs) -> Signal:
    """ Port Constructor. Thin wrapper around `hdl21.Signal`.
    The `direction` argument sets the Port's direction,
    and defaults to the unknown direction `PortDir.NONE`. """
    return Signal(direction=direction, vis=Visibility.PORT, **kwargs)


@connectable
@dataclass
class Slice:
    """ Signal Slice, comprising a subset of its width """

    signal: Signal
    top: int
    bot: int

    @property
    def width(self):
        return 1 + self.top - self.bot


@connectable
class Concat:
    """ Signal Concatenation
    Uses *HDL-convention* ordering, in which *MSBs* are specified first. """

    def __init__(self, *parts):
        for p in parts:
            if not isinstance(p, (Signal, Slice, Concat)):
                raise TypeError
        self.parts = parts

    @property
    def width(self):
        return sum([s.width for s in self.parts])


@connectable
@dataclass
class NoConn:
    """
    # No-Connect 
    
    Special placeholder connectable-object which indicates "unconnected" Ports,
    typically unconnected outputs.
    
    An optional `name` field allows guidance for external netlisting, 
    for cases in which consistent naming is desirable (e.g. for waveform probing). 
    """

    name: Optional[str] = None
