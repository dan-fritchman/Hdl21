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

from typing import Callable, Optional, Any, List
from enum import Enum
from dataclasses import field
from pydantic.dataclasses import dataclass

# Local imports
from .connect import connectable, is_connectable


class PortDir(Enum):
    """ Port-Direction Enumeration """

    INPUT = 0
    OUTPUT = 1
    INOUT = 2
    NONE = 3


class Visibility(Enum):
    """ Port-Visibility Enumeration """

    INTERNAL = 0  # Internal, Module-private Signal
    PORT = 1  # Exposed as a Port


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

        FIXME: this commentary reflects what *should* happen, not totally what *is* yet: 

        Signal slices are indexed "Python style", in the senses that: 
        * Negative indices are supported, and count from the "end" of the Signal.
        * Slice-ranges such as `sig[0:2]` are supported, and *inclusive* of the start, while *exclusive* of the end index. 
        * Negative-range slices such as `sig[2:0:-1]`, again *inclusive* of the start, *exclusive* of the end index, and *reversed*.
        Popular HDLs commonly use different signal-indexing conventions. 
        Hdl21's own primary exchange format (in ProtoBuf) does as well, 
        eschewing adopting inclusive-endpoints and eschewing negative-indexing.
        """

        if isinstance(key, int):
            if key >= self.width:
                raise ValueError(f"Out-of-bounds index {key} into {self}")
            if key < 0:
                key = key + self.width
            return Slice(signal=self, top=key, bot=key, step=1)

        if isinstance(key, slice):
            # Note these `slice` attributes are descriptor-things, and they get weird, fast.
            # Extracting their three key fields the most-hardest way via `__getattribute__` seems to work cleanest.
            start = slice.__getattribute__(key, "start")
            stop = slice.__getattribute__(key, "stop")
            step = slice.__getattribute__(key, "step")
            start = 0 if start is None else start
            stop = self.width - 1 if stop is None else stop
            step = 1 if step is None else step
            # Wrap around the start and stop to allow for negative slicing
            start = start if start >= 0 else self.width + start
            stop = stop if stop >= 0 else self.width + stop - 1
            if step == 0:
                raise ValueError(f"slice step cannot be zero")
            elif step < 0:
                # Align bot with the step
                top = start
                bot = start + (-(start - stop) // step) * step
            else:
                # Align top with the step
                top = start + -(-(stop - start) // step) * step
                bot = start
            if top > self.width:
                raise ValueError(f"Out-of-bounds index {top} into {self}")
            if bot > self.width:
                raise ValueError(f"Out-of-bounds index {bot} into {self}")
            if bot > top:
                raise ValueError(f"Invalid slice ({bot} > {top}) {key} into {self}")
            return Slice(signal=self, top=top, bot=bot, step=step)

        raise TypeError(f"Invalid slice-type {key} into {self}")


def Signals(num: int, **kwargs) -> List[Signal]:
    """ 
    Create `num` new Signals.  
    Typical usage: 
    ```python
    @h.module 
    class UsesSignals:
        bias, fold, mirror = h.Signals(3)
    ```
    Note the `num` value is required to support the tuple-destructuring use-case shown above. 
    """
    return _plural(fn=Signal, num=num, **kwargs)


def Input(**kwargs) -> Signal:
    """ Input Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(vis=Visibility.PORT, direction=PortDir.INPUT, **kwargs)


def Inputs(num: int, **kwargs) -> List[Signal]:
    """ 
    Create `num` new Input Ports.  
    Typical usage: 
    ```python
    @h.module 
    class UsesInputs:
        a, b, c, VDD, VSS = h.Inputs(5)
    ```
    Note the `num` value is required to support the tuple-destructuring use-case shown above. 
    """
    return _plural(fn=Input, num=num, **kwargs)


def Output(**kwargs) -> Signal:
    """ Output Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(vis=Visibility.PORT, direction=PortDir.OUTPUT, **kwargs)


def Outputs(num: int, **kwargs) -> List[Signal]:
    """ 
    Create `num` new Output Ports.  
    Typical usage: 
    ```python
    @h.module 
    class UsesOutputs:
        tdo, tms, tck = h.Outputs(3)
    ```
    Note the `num` value is required to support the tuple-destructuring use-case shown above. 
    """
    return _plural(fn=Output, num=num, **kwargs)


def Inout(**kwargs) -> Signal:
    """ Inout Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(vis=Visibility.PORT, direction=PortDir.INOUT, **kwargs)


def Inouts(num: int, **kwargs) -> List[Signal]:
    """ 
    Create `num` new Inout Ports.  
    Typical usage: 
    ```python
    @h.module 
    class UsesInouts:
        gpio1, gpio2 = h.Inouts(2)
    ```
    Note the `num` value is required to support the tuple-destructuring use-case shown above. 
    """
    return _plural(fn=Inout, num=num, **kwargs)


def Port(direction=PortDir.NONE, **kwargs) -> Signal:
    """ Port Constructor. Thin wrapper around `hdl21.Signal`.
    The `direction` argument sets the Port's direction,
    and defaults to the unknown direction `PortDir.NONE`. """
    return Signal(direction=direction, vis=Visibility.PORT, **kwargs)


def Ports(num: int, **kwargs) -> List[Signal]:
    """ 
    Create `num` new Ports.  
    Typical usage: 
    ```python
    @h.module 
    class UsesPorts:
        inp, out = h.Ports(2)
    ```
    Note the `num` value is required to support the tuple-destructuring use-case shown above. 
    """
    return _plural(fn=Port, num=num, **kwargs)


def _plural(*, fn: Callable, num: int, **kwargs) -> List[Signal]:
    """ Internal helper method for creating `num` identical `Signal` objects via callable `fn`. """
    rv = list()
    for _ in range(num):
        rv.append(fn(**kwargs))
    return rv


@connectable
@dataclass
class Slice:
    """ Signal Slice, comprising a subset of its width """

    signal: Signal  # Parent Signal
    top: int  # Top index (inclusive)
    bot: int  # Bottom index (inclusive)
    step: int  # Index step size

    @property
    def width(self) -> int:
        """ Slice width """
        if self.step != 1:
            raise NotImplementedError  # FIXME!
        return 1 + self.top - self.bot

    def __eq__(self, other: "Slice") -> bool:
        """ Slice equality requires *identity* between parent Signals """
        if not isinstance(other, Slice):
            return NotImplemented
        return (
            self.signal is other.signal
            and self.top == other.top
            and self.bot == other.bot
            and self.step == other.step
        )


@connectable
class Concat:
    """ Signal Concatenation
    Uses *Python-convention* ordering, in which "LSBs", i.e. index 0, are specified first. """

    def __init__(self, *parts):
        for p in parts:
            if not is_connectable(p):
                raise TypeError(f"Signal-concatenating unconnectable object {p}")
        self.parts = parts

    @property
    def width(self):
        return sum([s.width for s in self.parts])

    def __eq__(self, _other) -> bool:
        # Concat-equality can be implemented, but has plenty of edge cases
        # not yet worked through. For example slicing and re-concatenation:
        # ```python
        # s = h.Signal(width=2)      # Create a 2-bit signal
        # s == h.Concat(s[0], s[1])  # Slice and re-concatenate it
        # # Should that be True of False?
        # ```
        raise NotImplementedError


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
