"""
# Hdl21 Slices
By-index references into Connectable types. 
"""

from typing import Optional, Union, Any

# Local imports
from .datatype import datatype
from .connect import connectable
from .slices import slices, does_slices
from .signal import Signal
from .concat import Concat, concatable


@slices
@concatable
@connectable
@datatype
class Slice:
    """Signal Slice, comprising a subset of its width"""

    signal: Any  # Parent Signal/ Connectable
    top: int  # Top index (exclusive)
    bot: int  # Bottom index (inclusive)
    start: Optional[int]  # Python-convention start index
    stop: Optional[int]  # Python-convention stop index
    step: Optional[int]  # Python-convention step size

    index: Optional[Union[int, slice]] = None  # Python-convention index

    def __post_init_post_parse__(self):
        if not does_slices(self.signal):
            raise TypeError(f"{self.signal} is not Sliceable")

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

def assert_valid(self: Slice):
    # FIXME!
    if self.step is not None and self.step == 0:
        raise ValueError(f"Invalid Slice into {self.signal}: step==0")
    if self.width < 1:
        raise ValueError(f"Invalid Slice into {self.signal}: width={self.width}")
    if self.top <= self.bot:
        msg = f"Invalid Slice into {self.signal}: top={self.top} <= bot={self.bot}"
        raise ValueError(msg)


# Slice-compatible type aliases
# FIXME! got some to add
Sliceable = Union[Signal, Concat, Slice]
