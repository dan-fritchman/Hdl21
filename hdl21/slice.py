"""
# Hdl21 Slices
By-index references into Connectable types. 
"""

from copy import copy
from enum import Enum
from dataclasses import field
from typing import Callable, Optional, List, Union, Set
from pydantic.dataclasses import dataclass

# Local imports
from .connect import connectable
from .slices import slices
from .signal import Signal
from .concat import Concat, concatable


@slices
@concatable
@connectable
@dataclass
class Slice:
    """Signal Slice, comprising a subset of its width"""

    signal: "Sliceable"  # Parent Signal
    top: int  # Top index (exclusive)
    bot: int  # Bottom index (inclusive)
    start: Optional[int]  # Python-convention start index
    stop: Optional[int]  # Python-convention stop index
    step: Optional[int]  # Python-convention step size

    index: Optional[Union[int, slice]] = None  # Python-convention index

    def __post_init_post_parse__(self):
        if self.step is not None and self.step == 0:
            raise ValueError(f"Invalid Slice into {self.signal}: step==0")
        if self.width < 1:
            raise ValueError(f"Invalid Slice into {self.signal}: width={self.width}")
        if self.top <= self.bot:
            msg = f"Invalid Slice into {self.signal}: top={self.top} <= bot={self.bot}"
            raise ValueError(msg)

    @property
    def width(self) -> int:
        """Slice Width Accessor"""
        step = 1 if self.step is None else abs(self.step)
        return (self.top - self.bot) // step

    def __eq__(self, other: "Slice") -> bool:
        """Slice equality requires *identity* between parent Signals"""
        if not isinstance(other, Slice):
            return NotImplemented
        return (
            self.signal is other.signal
            and self.top == other.top
            and self.bot == other.bot
            and self.step == other.step
        )


# Slice-compatible type aliases
Sliceable = Union[Signal, Concat, Slice]

Slice.__pydantic_model__.update_forward_refs()
