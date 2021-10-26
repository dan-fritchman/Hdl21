"""
# Hdl21 Differential Bundle and Facilities for Differential Circuits 

"""

from pydantic.dataclasses import dataclass

# Local imports
from .signal import Signal
from .bundle import bundle
from .instantiable import Instantiable


@bundle
class DiffSomething:
    """ Differential Bundle """

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

