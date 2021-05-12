"""
# hdl21 Signals 
"""

from typing import Optional
from enum import Enum
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
    Th base-level unit of hardware connectivity 
    """

    name: Optional[str] = None
    width: int = 1
    visibility: Visibility = Visibility.INTERNAL
    direction: PortDir = PortDir.NONE
    src: Optional[Enum] = None
    dest: Optional[Enum] = None


def Input(**kwargs) -> Signal:
    """ Input Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(visibility=Visibility.PORT, direction=PortDir.INPUT, **kwargs)


def Output(**kwargs) -> Signal:
    """ Output Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(visibility=Visibility.PORT, direction=PortDir.OUTPUT, **kwargs)


def Inout(**kwargs) -> Signal:
    """ Inout Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(visibility=Visibility.PORT, direction=PortDir.INOUT, **kwargs)


def Port(**kwargs) -> Signal:
    """ Port Constructor. Thin wrapper around `hdl21.Signal` """
    return Signal(visibility=Visibility.PORT, direction=PortDir.NONE, **kwargs)
