"""
Type-alias for `Instantiable` hdl21 types. Each is valid as the `of` field of `hdl21.Instance`s, 
and thus supports its "connect by call" and "connect by assignment" semantics. 
"""

import copy
from typing import Any, Union, Dict

from .module import Module
from .primitives import PrimitiveCall
from .external_module import ExternalModuleCall


# Instantiable types-union
Instantiable = Union[Module, ExternalModuleCall, PrimitiveCall]


def is_instantiable(val: Any) -> bool:
    """Boolean indication of whether `val` is an `Instantiable` type."""
    return isinstance(val, Instantiable.__args__)


def qualname(i: Instantiable) -> str:
    """Path-qualified name of Instantiable `i`"""
    from .qualname import qualname as module_qualname

    if isinstance(i, PrimitiveCall):
        # These have no "qualification" paths, just a singular name.
        return i.name

    # The other variants can have a path-qualifier
    if isinstance(i, Module):
        return module_qualname(i)
    if isinstance(i, ExternalModuleCall):
        return module_qualname(i.module)

    raise TypeError(f"Invalid Instantiable {i}")


def io(i: Instantiable) -> Dict[str, "Connectable"]:
    """
    Get a complete dictionary of IO ports for `i`, including all types: Signals and Bundles.
    Copies the Instantiable's top-level dictionary so that it is not modified by consumers.
    """

    rv = copy.copy(i.ports)
    if hasattr(i, "bundle_ports"):
        rv.update(copy.copy(i.bundle_ports))
    return rv


__all__ = ["Instantiable", "is_instantiable"]
