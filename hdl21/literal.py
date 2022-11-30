from typing import Optional
from pydantic.dataclasses import dataclass


@dataclass
class Literal:
    """
    # Literal
    A thin wrapper around a string, generally to be used outside Hdl21, e.g. in external netlists.
    """

    txt: str  # String literal text
    name: Optional[str] = None  # Attribute name, when used in a class
