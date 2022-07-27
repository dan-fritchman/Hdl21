"""
# Hdl21 Slices
By-index references into Connectable types. 
"""

from typing import Optional, Union, Any, Set
from weakref import WeakSet

# Local imports
from .datatype import datatype
from .connect import connectable
from .slices import slices, does_slices
from .signal import Signal
from .concat import Concat, concatable


@datatype
class SliceInner:
    top: int  # Top index (exclusive)
    bot: int  # Bottom index (inclusive)
    start: Optional[int]  # Python-convention start index
    stop: Optional[int]  # Python-convention stop index
    step: Optional[int]  # Python-convention step size
    width: int


@slices
@concatable
@connectable
@datatype
class Slice:
    """Signal Slice, comprising a subset of its width"""

    signal: Any  # Parent Signal/ Connectable
    index: Optional[Union[int, slice]] = None  # Python index, passed to square brackets

    def __post_init_post_parse__(self):
        if not does_slices(self.signal):
            raise TypeError(f"{self.signal} is not Sliceable")
        self.connected_ports: Set["PortRef"] = set()
        self._inner: Optional[SliceInner] = None
        self._slices: WeakSet["Slice"] = set()
        self._concats: WeakSet["Concat"] = set()

    @property
    def top(self) -> int:
        if self._inner is None:
            self._inner = _slice_inner(self)
        return self._inner.top

    @property
    def bot(self) -> int:
        if self._inner is None:
            self._inner = _slice_inner(self)
        return self._inner.bot

    @property
    def start(self) -> int:
        if self._inner is None:
            self._inner = _slice_inner(self)
        return self._inner.start

    @property
    def stop(self) -> int:
        if self._inner is None:
            self._inner = _slice_inner(self)
        return self._inner.stop

    @property
    def step(self) -> int:
        if self._inner is None:
            self._inner = _slice_inner(self)
        return self._inner.step

    @property
    def width(self) -> int:
        if self._inner is None:
            self._inner = _slice_inner(self)
        return self._inner.width

    def __eq__(self, other) -> bool:
        # Identity is equality
        return id(self) == id(other)

    def __hash__(self) -> bool:
        # Identity is equality
        return hash(id(self))


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


def _slice_inner(slize: Slice) -> SliceInner:
    """Square-bracket slicing into Signals, Concatenations, and Slices.
    Assuming valid inputs, returns a signal-`Slice`.

    Signal slices are indexed "Python style", in the senses that:
    * Negative indices are supported, and count from the "end" of the Signal.
    * Slice-ranges such as `sig[0:2]` are supported, and *inclusive* of the start, while *exclusive* of the end index.
    * Negative-range slices such as `sig[2:0:-1]`, again *inclusive* of the start, *exclusive* of the end index, and *reversed*.
    Popular HDLs commonly use different signal-indexing conventions.
    Hdl21's own primary exchange format (in ProtoBuf) does as well,
    eschewing adopting inclusive-endpoints and negative-indexing.
    """

    parent = slize.signal
    index = slize.index

    if isinstance(index, int):
        if index >= parent.width:
            raise ValueError(f"Out-of-bounds index {index} into {parent}")
        if index < 0:
            index += parent.width
        return SliceInner(
            top=index + 1, bot=index, start=index, stop=None, step=None, width=1
        )

    if isinstance(index, slice):
        # Note these `slice` attributes are descriptor-things, and they get weird, fast.
        # Extracting their three index fields the most-hardest way via `__getattribute__` seems to work cleanest.
        start = slice.__getattribute__(index, "start")
        stop = slice.__getattribute__(index, "stop")
        step = slice.__getattribute__(index, "step")

        stepsz = 1 if step is None else step
        if stepsz == 0:
            raise ValueError(f"slice step cannot be zero")
        elif stepsz < 0:
            # Here `top` gets a "+1" since `start` is *inclusive*, while `bot` gets "+1" as `stop` is *exclusive*.
            top = (
                parent.width
                if start is None
                else start + 1
                if start >= 0
                else parent.width + start + 1
            )
            bot = (
                0
                if stop is None
                else stop + 1
                if stop >= 0
                else parent.width + stop + 1
            )
            # Align bot with the step
            bot += (top - bot) % abs(stepsz)
        else:
            # Here `start` and `stop` match `top` and `bot`'s inclsive/ exclusivity.
            # No need to add any offsets.
            top = (
                parent.width
                if stop is None
                else stop
                if stop >= 0
                else parent.width + stop
            )
            bot = 0 if start is None else start if start >= 0 else parent.width + start
            # Align top with the step
            top -= (top - bot) % stepsz

        width = (top - bot) // stepsz

        # Create and return our Slice. More checks are done in its constructor.
        return SliceInner(
            top=top, bot=bot, step=step, start=start, stop=stop, width=width
        )

    raise RuntimeError("Internal Error: Slice index should be an int or (python) slice")
