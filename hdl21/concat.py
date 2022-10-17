"""
# Hdl21 Concatenations 
"Sequences" of Signals and other Connectable objects. 
"""

from typing import Optional, Set

# Local imports
from .connect import connectable
from .sliceable import sliceable
from .concatable import concatable, is_concatable


@sliceable
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
        self._connected_ports: Set["PortRef"] = set()
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
        # FIXME: whether to keep me around as a property
        # As is the elaboration mechanics do not use this property, but users may.
        from .elab.elaborators.width import width

        return width(self)


__all__ = ["Concat"]
