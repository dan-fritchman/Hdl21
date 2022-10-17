"""
# Width Resolution Helper 

Function to determine the `width` of connectable types. 
"""

# Std-Lib Imports
from typing import Union, Callable

# Local imports
from ...connect import Connectable
from ...portref import PortRef
from ...signal import Signal
from ...slice import Slice
from ...concat import Concat
from ...noconn import NoConn
from ...bundle import (
    AnonymousBundle,
    BundleInstance,
    BundleRef,
)
from .resolve_ref_types import resolve_bundleref_type, resolve_portref_type

# HasWidth & Sliceable Type Uhions
# Everything that has, or at least sometimes has, an integer Signal-style `width`.
# AND everything that can be `Slice`d.
# These happen to be the same set of types, but can be broken up
# if the two should ever differ.
Sliceable = HasWidth = Union[Signal, Slice, Concat, BundleRef, PortRef]


def fail(msg: str) -> None:
    # The default failure handler
    raise RuntimeError(msg)


def width(conn: Connectable, failer: Callable = fail) -> int:
    """Get the `width` of a conn. Largely dispatches across conn types.
    Optional function-valued argument `failer` is passed all errors.
    This is commonly used to pass failure information and control back to `Elaborator`s."""

    # A reminder, as of this writing:
    # Connectable = Union["Signal", "Slice", "Concat", "NoConn", "PortRef", "BundleInstance", "AnonymousBundle", "BundleRef"]
    # (Man that Rust-style enum would be nice)

    # Invalid cases
    if isinstance(conn, (BundleInstance, AnonymousBundle, NoConn)):
        return failer(f"Invalid `width` of {conn}")

    # Typical "scalar" cases
    if isinstance(conn, Signal):
        return conn.width
    if isinstance(conn, Slice):
        return conn.width
    if isinstance(conn, Concat):
        return sum([width(p) for p in conn.parts])

    # References
    if isinstance(conn, (BundleRef, PortRef)):
        return ref_width(conn, failer)

    return failer(f"Invalid `width` of {conn}")


def ref_width(ref: Union[PortRef, BundleRef], failer: Callable = fail) -> int:
    """Get a reference's width from its referent.
    Fail if this resolves to a Bundle Instance.
    And cache the result on the Ref for future use.

    Optional function-valued argument `failer` is passed all errors.
    This is commonly used to pass failure information and control back to `Elaborator`s."""

    if ref._width is not None:
        return ref._width

    # Get the referent
    if isinstance(ref, BundleRef):
        referent = resolve_bundleref_type(ref, failer)
    elif isinstance(ref, PortRef):
        referent = resolve_portref_type(ref)
    else:
        return failer(f"Invalid arg to ref_width {ref}")

    # And get its width
    if isinstance(referent, Signal):
        ref._width = width(referent, failer)
        return ref._width
    if isinstance(referent, BundleInstance):
        return failer(f"Invalid `width` of Bundle {referent}")
    return failer(f"Invalid `width` of {referent}")
