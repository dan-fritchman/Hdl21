# PyPi Imports
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Literal:
    """
    # Literal
    A thin wrapper around a string, generally to be used outside Hdl21, e.g. in external netlists.
    """

    text: str  # String literal text


__doc__ = Literal.__doc__
