"""
Type-alias for `Instantiable` hdl21 types. Each is valid as the `of` field of `hdl21.Instance`s, 
and thus supports its "connect by call" and "connect by assignment" semantics. 
"""

import copy
from typing import Any, Union, Dict

from pydantic import BaseModel

from .datatype import AllowArbConfig
from .module import Module
from .primitives import PrimitiveCall
from .external_module import ExternalModuleCall


# Instantiable types-union
InstantiableUnion = Union[Module, ExternalModuleCall, PrimitiveCall]


class Instantiable(BaseModel):
    """
    # Instantiable

    Generally this means
    ````python
    Union[Module, ExternalModuleCall, PrimitiveCall]
    ```
    with some customized checking and error handling.
    """

    __root__: InstantiableUnion
    Config = AllowArbConfig

    def __init__(self, *_, **__):
        # Brick any attempts to create instances
        msg = f"Invalid attempt to instantiate an `Instantiable` directly. "
        raise RuntimeError(msg)

    @classmethod
    def __get_validators__(cls):
        yield assert_instantiable


def assert_instantiable(i: Any) -> Instantiable:
    """# Assert that `i` is an `Instantiable` type."""
    if not is_instantiable(i):
        return invalid(i)
    return i


def is_instantiable(val: Any) -> bool:
    """Boolean indication of whether `val` is an `Instantiable` type."""
    return isinstance(val, InstantiableUnion.__args__)


def invalid(val: Any) -> None:
    """Raise a `TypeError` with debug info for invalid `Instantiable` `val`."""

    # Give more specific error-messages for our common types.
    # Especially those that are easily confused, e.g. `Primitive`, `ExternalModule`, and `Generator`
    from .external_module import ExternalModule
    from .primitives import Primitive
    from .generator import Generator
    from .instance import _Instance

    msg = f"Invalid `Instantiable` {val} of type {type(val)}.\n"
    if isinstance(val, (Generator, Primitive, ExternalModule)):
        msg += f"Did you mean to *call it* to apply parameters first?"
    elif isinstance(val, _Instance):
        msg += f"Did you mean to use its target module `{val.of}` instead?"
    else:  # Generic message for everything else
        msg += f"Valid `Instantiable` types include: {list(InstantiableUnion.__args__)}"
    raise TypeError(msg)


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
