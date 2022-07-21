"""
# Slice-Enabling Decorator
"""
from copy import copy
from enum import Enum
from dataclasses import field
from typing import Callable, Optional, Any, List, Union, Set
from pydantic.dataclasses import dataclass

# Local imports
from .connect import is_connectable


def slices(cls: type) -> type:
    """Decorator to add the 'square-bracket indexing produces `Slice`s' behavior."""

    if getattr(cls, "__getitem__", None) is not None:
        msg = f"Internal hdl21 Error: invavlid `slices`-decoration of {cls} with existing __getitem__"
        raise RuntimeError(msg)

    if not is_connectable(cls):
        msg = f"Internal hdl21 Error: invavlid `slices`-decoration of {cls} which is not `connectable`"
        raise RuntimeError(msg)

    def __getitem__(self, key: Any) -> "Slice":
        return _slice_(parent=self, key=key)

    # Add the new behavior to the class
    cls.__getitem__ = __getitem__
    cls.__getitem__.__doc__ = _slice_.__doc__
    # And don't forget to return that class!
    return cls


def _slice_(*, parent: "Sliceable", key: Union[int, slice]) -> "Slice":
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

    from .slice import Slice

    if isinstance(key, int):
        if key >= parent.width:
            raise ValueError(f"Out-of-bounds index {key} into {parent}")
        if key < 0:
            key += parent.width
        return Slice(
            signal=parent, top=key + 1, bot=key, start=key, stop=None, step=None
        )

    if isinstance(key, slice):
        # Note these `slice` attributes are descriptor-things, and they get weird, fast.
        # Extracting their three key fields the most-hardest way via `__getattribute__` seems to work cleanest.
        start = slice.__getattribute__(key, "start")
        stop = slice.__getattribute__(key, "stop")
        step = slice.__getattribute__(key, "step")

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

        # Create and return our Slice. More checks are done in its constructor.
        return Slice(signal=parent, top=top, bot=bot, step=step, start=start, stop=stop)

    raise TypeError(f"Invalid slice-type {key} into {parent}")
