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
from .role import Role
from .datatype import datatype
from .visibility import Visibility
from .connect import connectable
from .sliceable import sliceable
from .concat import concatable
from .props import Properties


class PortDir(Enum):
    """# Port Direction Enumeration"""

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    INOUT = "INOUT"
    NONE = "NONE"  # No direction or unspecified

    def flipped(self) -> "PortDir":
        """# Flip the direction of a port"""
        if self == PortDir.INPUT:
            return PortDir.OUTPUT
        if self == PortDir.OUTPUT:
            return PortDir.INPUT
        return self  # INOUT or NONE


class Usage(Enum):
    """# Signal Usage"""

    SIGNAL = "SIGNAL"
    POWER = "POWER"
    GROUND = "GROUND"
    CLOCK = "CLOCK"


@sliceable
@concatable
@connectable
@datatype
class Signal:
    """
    # Signal

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

    name: Optional[str] = None  # Signal name
    width: int = 1  # Bit-width
    vis: Visibility = field(repr=False, default=Visibility.INTERNAL)  # Port visibility
    direction: PortDir = field(repr=False, default=PortDir.NONE)  # Port direction
    usage: Usage = field(repr=False, default=Usage.SIGNAL)  # Signal usage
    props: Properties = field(repr=False, default_factory=Properties)  # Properties
    desc: Optional[str] = None  # Description
    src: Optional[Role] = field(repr=False, default=None)  # Source Role
    dest: Optional[Role] = field(repr=False, default=None)  # Destination Role

    # Related signals
    related_clk: Optional["Signal"] = field(repr=False, default=None)
    # Related clock signal
    related_pwr: Optional["Signal"] = field(repr=False, default=None)
    # Related power signal
    related_gnd: Optional["Signal"] = field(repr=False, default=None)
    # Related ground signal

    def __post_init_post_parse__(self):
        if self.width < 1:
            raise ValueError(f"Signal {self.name} width must be positive")
        self._parent_module: Optional["Module"] = None
        self._slices: Set["Slice"] = set()
        self._concats: Set["Concat"] = set()
        self._connected_ports: Set["PortRef"] = set()

        # Back-references to related signals
        self._related_clk_of: Set["Signal"] = set()
        self._related_pwr_of: Set["Signal"] = set()
        self._related_gnd_of: Set["Signal"] = set()

        # Add those back-references to signals *we* relate to.
        # Note this only happens at construction-time.
        if self.related_clk is not None:
            self.related_clk._related_clk_of.add(self)
        if self.related_pwr is not None:
            self.related_pwr._related_pwr_of.add(self)
        if self.related_gnd is not None:
            self.related_gnd._related_gnd_of.add(self)

    def __eq__(self, other) -> bool:
        # Identity is equality
        return other is self

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

    def __rmul__(self, num: int) -> List["Signal"]:
        """# Right multiplication. Creates `num` copies of this Signal."""
        if not isinstance(num, int):
            return NotImplemented
        return [copy(self) for _ in range(num)]


"""
# Constructor Helpers 

Thin wrappers around the `Signal` constructor which set common fields, 
e.g. `Port()` replacing `Signal(vis=Visibility.PORT)`.
"""


def Input(**kwargs) -> Signal:
    """# Input Port Constructor
    Thin wrapper around `hdl21.Signal`"""
    return Signal(vis=Visibility.PORT, direction=PortDir.INPUT, **kwargs)


def Output(**kwargs) -> Signal:
    """# Output Port Constructor
    Thin wrapper around `hdl21.Signal`"""
    return Signal(vis=Visibility.PORT, direction=PortDir.OUTPUT, **kwargs)


def Inout(**kwargs) -> Signal:
    """# Inout Port Constructor
    Thin wrapper around `hdl21.Signal`"""
    return Signal(vis=Visibility.PORT, direction=PortDir.INOUT, **kwargs)


def Port(direction=PortDir.NONE, **kwargs) -> Signal:
    """# Port Constructor
    Thin wrapper around `hdl21.Signal`.
    The `direction` argument sets the Port's direction,
    and defaults to the unknown direction `PortDir.NONE`."""
    return Signal(direction=direction, vis=Visibility.PORT, **kwargs)


def Power(**kwargs) -> Signal:
    """# Power Signal Constructor
    Thin wrapper around `hdl21.Signal`"""
    return Signal(usage=Usage.POWER, **kwargs)


def Ground(**kwargs) -> Signal:
    """# Ground Signal Constructor
    Thin wrapper around `hdl21.Signal`"""
    return Signal(usage=Usage.GROUND, **kwargs)


def Clock(**kwargs) -> Signal:
    """# Clock Signal Constructor
    Thin wrapper around `hdl21.Signal`"""
    return Signal(usage=Usage.CLOCK, **kwargs)


"""
# Plural Constructors

Wrappers that generate the functions named `Signals`, `Ports`, and the like. 
"""


def _pluralize(fn: Callable):
    """Inner helper method for creating "plural" versions of `Signal` constructors."""

    def _plural(num: int, **kwargs) -> List[Signal]:
        return [fn(**kwargs) for _ in range(num)]

    # Give the wrapper a plural name, e.g. "Signals" or "Clocks"
    _plural.__name__ = fn.__name__ + "s"
    # And a basic doc string
    _plural.__doc__ = f"Create `num` new {fn.__name__}s."
    # Add the wrapper to this module's namespace
    globals()[_plural.__name__] = _plural


# Create all those plural versions
[_pluralize(fn) for fn in [Signal, Port, Input, Output, Inout, Power, Ground, Clock]]


"""
# Non-public (well, at least in intent) Methods
"""


def _copy_to_internal(sig: Signal) -> Signal:
    """Make a copy of `sig`, replacing its visibility and port-direction to be internal."""
    sig = copy(sig)
    sig.vis = Visibility.INTERNAL
    sig.direction = PortDir.NONE
    sig._parent_module = None
    return sig
