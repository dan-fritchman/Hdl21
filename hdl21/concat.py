"""
# Hdl21 Concatenations 
"Sequences" of Signals and other Connectable objects. 
"""

from copy import copy
from enum import Enum
from dataclasses import field
from typing import Callable, Optional, Any, List, Union, Set
from pydantic.dataclasses import dataclass

# Local imports
from .connect import connectable, is_connectable
from .portref import PortRef
from .slices import slices


def concatable(cls: type) -> type:
    """Decorator for `Concat`-compatible types."""
    if not is_connectable(cls):
        raise TypeError(f"{cls} is not connectable")
    # Just adds a "marker trait" to the class
    cls.__concatable__ = True
    return cls


def is_concatable(obj: object) -> type:
    return getattr(obj, "__concatable__", False)


@slices
@concatable
@connectable
class Concat:
    """Signal Concatenation
    Uses *Python-convention* ordering, in which "LSBs", i.e. index 0, are specified first."""

    def __init__(self, *parts):
        invalid_parts = [p for p in parts if not is_concatable(p)]
        if invalid_parts:
            raise TypeError(f"Invalid `Concat` of {invalid_parts}")

        # Store the `parts` to a tuple
        self.parts = tuple(parts)

    def __eq__(self, _other) -> bool:
        # Concat-equality can be implemented, but has plenty of edge cases
        # not yet worked through. For example slicing and re-concatenation:
        # ```python
        # s = h.Signal(width=2)      # Create a 2-bit signal
        # s == h.Concat(s[0], s[1])  # Slice and re-concatenate it
        # # Should that be True of False?
        # ```
        return NotImplemented

    def __repr__(self):
        return f"Concat(parts={len(self.parts)})"

    @property
    def width(self):
        # FIXME!
        return width(self)


def assert_valid(concat: Concat):
    # FIXME!
    if self.width < 1:
        raise ValueError(f"Invalid Zero-Width Concat of {self.parts}")


def width(concat: Concat) -> int:
    # FIXME!
    return sum([s.width for s in concat.parts])


__all__ = ["Concat"]
