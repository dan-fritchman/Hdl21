"""
Type-alias for `Instantiable` hdl21 types. Each is valid as the `of` field of `hdl21.Instance`s, 
and thus supports its "connect by call" and "connect by assigment" semantics. 
"""

import copy
from typing import Any, Union, Dict

from .module import Module
from .external_module import ExternalModuleCall
from .generator import GeneratorCall
from .primitives import PrimitiveCall


# Instantiable types-union
Instantiable = Union[Module, ExternalModuleCall, GeneratorCall, PrimitiveCall]


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
    if isinstance(i, GeneratorCall):
        return module_qualname(i.result)
    raise TypeError


def io(i: Instantiable) -> Dict[str, "Connectable"]:
    """Get a complete dictionary of IO ports for `i`, including all types: Signals and Bundles.
    Copies the Instantiable's top-level dictionary so that it is not modified by consumers."""

    if isinstance(i, GeneratorCall):
        if i.result is None:
            raise RuntimeError(f"Cannot get IO of unelaborated Generator {i}")
        # Take the result of the generator call
        i = i.result

    rv = copy.copy(i.ports)
    if hasattr(i, "bundle_ports"):
        rv.update(copy.copy(i.bundle_ports))
    return rv


__all__ = ["Instantiable", "is_instantiable"]
