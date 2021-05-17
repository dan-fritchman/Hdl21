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

from typing import Optional
from enum import Enum
from dataclasses import field
from pydantic.dataclasses import dataclass

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
    src: Optional[Enum] = field(repr=False, default=None)
    dest: Optional[Enum] = field(repr=False, default=None)

    def __post_init_post_parse__(self):
        if self.width < 1:
            raise ValueError


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
