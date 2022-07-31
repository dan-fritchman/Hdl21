"""
# Slice-Enabling Decorator
"""

from typing import Union


def slices(cls: type) -> type:
    """Decorator to add the 'square-bracket indexing produces `Slice`s' behavior."""
    from .connect import is_connectable

    if getattr(cls, "__getitem__", None) is not None:
        msg = f"Internal hdl21 Error: invavlid `slices`-decoration of {cls} with existing __getitem__"
        raise RuntimeError(msg)

    if not is_connectable(cls):
        msg = f"Internal hdl21 Error: invavlid `slices`-decoration of {cls} which is not `connectable`"
        raise RuntimeError(msg)

    def __getitem__(self, index: Union[int, slice]) -> "Slice":
        return _slice_(parent=self, index=index)

    # Add the new behavior to the class
    cls.__getitem__ = __getitem__
    cls.__getitem__.__doc__ = _slice_.__doc__
    # And a marker attribute
    cls.__slices__ = True
    # And don't forget to return that class!
    return cls


def does_slices(obj: object) -> bool:
    """Returns True if the class has the `slices` decorator."""
    return getattr(obj, "__slices__", False)


def _slice_(*, parent: "Sliceable", index: Union[int, slice]) -> "Slice":
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

    if not isinstance(index, (int, slice)):
        raise TypeError

    slize = Slice(signal=parent, index=index)
    parent._slices.add(slize)
    return slize
