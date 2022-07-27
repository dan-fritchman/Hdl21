"""
# Hdl21 Concatenations 
"Sequences" of Signals and other Connectable objects. 
"""

from typing import Optional, Set

# Local imports
from .connect import connectable, is_connectable
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

        for part in parts:
            part._concats.add(self)

        # Store the `parts` to a tuple
        self.parts = tuple(parts)

        # Inner management data
        self.connected_ports: Set["PortRef"] = set()
        self._width: Optional[int] = None
        self._slices: Set["Slice"] = set()
        self._concats: Set["Concat"] = set()

    def __eq__(self, other) -> bool:
        # Identity is equality
        return id(self) == id(other)

    def __hash__(self) -> bool:
        # Identity is equality
        return hash(id(self))

    def __repr__(self):
        return f"Concat(parts={len(self.parts)})"

    @property
    def width(self):
        if self._width is None:
            self._width = width(self)
        return self._width


# FIXME: move!
def width(concat: Concat) -> int:
    width = sum([s.width for s in concat.parts])
    if width < 1:
        raise ValueError(f"Invalid Width Concat of {concat}")
    return width


__all__ = ["Concat"]

