"""
Type-alias for `Instantiable` hdl21 types. Each is valid as the `of` field of `hdl21.Instance`s, 
and thus supports its "connect by call" and "connect by assigment" semantics. 
"""

from typing import Any, Union, get_args

from .module import Module, ExternalModuleCall
from .generator import GeneratorCall
from .primitives import PrimitiveCall


# Instantiable types-union
Instantiable = Union[Module, ExternalModuleCall, GeneratorCall, PrimitiveCall]


def _is_instantiable(val: Any) -> bool:
    """ Boolean indication of whether `val` is an `Instantiable` type. """
    return isinstance(val, get_args(Instantiable))
