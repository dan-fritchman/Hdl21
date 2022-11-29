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

from copy import copy
from enum import Enum
from dataclasses import field
from typing import Callable, Optional, List, Set

# Local imports
from .datatype import datatype
from .connect import connectable
from .sliceable import sliceable
from .concat import concatable


class PortDir(Enum):
    """Port-Direction Enumeration"""

    INPUT = 0
    OUTPUT = 1
    INOUT = 2
    NONE = 3


class Visibility(Enum):
    """Port-Visibility Enumeration"""

    INTERNAL = 0  # Internal, Module-private Signal
    PORT = 1  # Exposed as a Port


@sliceable
@concatable
@connectable
@datatype
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
            raise ValueError(f"Signal {self.name} width must be positive")
        self._parent_module: Optional["Module"] = None
        self._slices: Set["Slice"] = set()
        self._concats: Set["Concat"] = set()
        self._connected_ports: Set["PortRef"] = set()

    def __eq__(self, other) -> bool:
        # Identity is equality
        return id(self) == id(other)

    def __hash__(self) -> bool:
        # Identity is equality
        return hash(id(self))

    def __copy__(self) -> "Signal":
        """Signal copying implementation
        Keeps "public" fields such as name and width,
        while dropping "per-module" fields such as `_slices`."""
        # Notably `_parent_module` *is not* copied.
        # It will generally be set when the copy is added to any new Module.
        return Signal(
            name=self.name,
            width=self.width,
            vis=self.vis,
            direction=self.direction,
            desc=self.desc,
            src=self.src,
            dest=self.dest,
        )

    def __deepcopy__(self, _memo) -> "Signal":
        """Signal "deep" copies"""
        # The same as shallow ones; there is no "deep" data being copied.
        return self.__copy__()


def _copy_to_internal(sig: Signal) -> Signal:
    """Make a copy of `sig`, replacing its visibility and port-direction to be internal."""
    sig = copy(sig)
    sig.vis = Visibility.INTERNAL
    sig.direction = PortDir.NONE
    sig._parent_module = None
    return sig


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
    """Input Port Constructor. Thin wrapper around `hdl21.Signal`"""
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
    """Output Port Constructor. Thin wrapper around `hdl21.Signal`"""
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
    """Inout Port Constructor. Thin wrapper around `hdl21.Signal`"""
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
    """Port Constructor. Thin wrapper around `hdl21.Signal`.
    The `direction` argument sets the Port's direction,
    and defaults to the unknown direction `PortDir.NONE`."""
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
    """Internal helper method for creating `num` identical `Signal` objects via callable `fn`."""
    rv = list()
    for _ in range(num):
        rv.append(fn(**kwargs))
    return rv
