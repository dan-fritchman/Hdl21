"""
# Hdl21 Differential Interface and Facilities for Differential Circuits 

"""

from pydantic.dataclasses import dataclass

# Local imports
from .signal import Signal
from .interface import interface
from .instantiable import Instantiable


@interface
class DiffSomething:
    """ Differential Interface """

    p = Signal(width=1, desc="Positive")
    n = Signal(width=1, desc="Negative")


@dataclass
class DiffSomethingElse:
    """ Differential Instance Bundle """

    of: Instantiable  # Target Module
    conns: Dict[str, Any]  # Really [str, Connectable]


def diff_inst(of: Instantiable) -> DiffSomethingElse:
    """ Create a Differential Instance Bundle """
    return DiffSomethingElse(of=of, conns={})

