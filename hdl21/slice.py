"""
# Hdl21 Slices

References by numeric index into Signals and other Connectable types. 
"""

from typing import Optional, Union, Any, Set
from weakref import WeakSet

# Local imports
from .datatype import datatype
from .connect import connectable
from .sliceable import sliceable, is_sliceable
from .concat import concatable


@sliceable
@concatable
@connectable
@datatype
class Slice:
    """
    # Slice

    Subset of the indices of a parent `Connectable`,
    commonly Signals, Concatenations, and other Slices.
    Typically produced via square-bracket indexing into said `Connectable`s.

    Hdl21 slices are indexed "Python style", in the senses that:
    * Negative indices are supported, and count from the "end" of the Signal.
    * Slice-ranges such as `sig[0:2]` are supported, and *inclusive* of the start, while *exclusive* of the end index.
    * Negative-range slices such as `sig[2:0:-1]`, again *inclusive* of the start, *exclusive* of the end index, and *reversed*.

    Popular HDLs commonly use different signal-indexing conventions.
    Hdl21's own primary exchange format (in ProtoBuf) does as well,
    eschewing adopting inclusive-endpoints and negative-indexing.
    """

    # Parent Connectable.
    # Really of union-type `Sliceable`, which is more painful to type-check statically,
    # although the constructor does it procedurally.
    parent: Any
    # Python index, i.e. that passed to square brackets
    index: Union[int, slice]

    def __post_init_post_parse__(self):
        if not is_sliceable(self.parent):
            raise TypeError(f"{self.parent} is not Sliceable")
        self._connected_ports: Set["PortRef"] = set()
        self._inner: Optional[SliceInner] = None
        self._slices: WeakSet[Slice] = set()
        self._concats: WeakSet["Concat"] = set()

    @property
    def top(self) -> int:
        return _get_inner(self).top

    @property
    def bot(self) -> int:
        return _get_inner(self).bot

    @property
    def step(self) -> int:
        return _get_inner(self).step

    @property
    def width(self) -> int:
        return _get_inner(self).width

    def __repr__(self):
        return f"Slice(parent={self.parent}, index={self.index})"

    def __eq__(self, other) -> bool:
        # Identity is equality
        return id(self) == id(other)

    def __hash__(self) -> bool:
        # Identity is equality
        return hash(id(self))


@datatype
class SliceInner:
    """Inner, private, resolved attributes of a `Slice`.
    Designed solely to be created by `_slice_inner` and stored as the `Slice._inner` field."""

    top: int  # Top index (exclusive)
    bot: int  # Bottom index (inclusive)
    step: int  # Python-convention step size
    width: int


def _slice_inner(slize: Slice) -> SliceInner:
    """Calculate the inner resolved fields for `slize`"""

    parent = slize.parent
    index = slize.index

    if isinstance(index, int):
        if index >= parent.width:
            raise ValueError(f"Out-of-bounds index {index} into {parent}")
        if index < 0:
            index += parent.width
        return SliceInner(top=index + 1, bot=index, step=1, width=1)

    if isinstance(index, slice):
        # Note these `slice` attributes are descriptor-things, and they get weird, fast.
        # Extracting their three index fields the most-hardest way via `__getattribute__` seems to work cleanest.
        start = slice.__getattribute__(index, "start")
        stop = slice.__getattribute__(index, "stop")
        step = slice.__getattribute__(index, "step")

        step = 1 if step is None else step
        if step == 0:
            raise ValueError(f"slice step cannot be zero")
        elif step < 0:
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
            bot += (top - bot) % abs(step)
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
            top -= (top - bot) % step

        width = (top - bot) // step

        # Create and return our Slice. More checks are done in its constructor.
        return SliceInner(top=top, bot=bot, step=step, width=width)

    # Shouldn't be reachable, but blow up if we (somehow) get here.
    raise TypeError("Internal Error: Slice index should be an int or (python) slice")


def _get_inner(slice: Slice) -> SliceInner:
    """Get a slice's `SliceInner`, calculating it inline if necessary"""
    if slice._inner is None:
        slice._inner = _slice_inner(slice)
    return slice._inner
