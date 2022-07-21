"""
# Param-Class Argument Calls

Enables the "no paramclass constructor" style invocation for Generators, ExternalModules, and Primitives.
Creates an instance of the generator's parameter-class if keyword args were provided instead.
If both were provided, fail.
"""

from typing import Optional, Union, Any, Dict

# Local Imports
from .default import Default


Callee = Union["Generator", "ExternalModule", "Primitive"]


def param_call(callee: Callee, arg: Any = Default, **kwargs: Dict) -> "Callee.Params":
    """
    # Param-Class Argument Calls

    Enables the "no paramclass constructor" style invocation for Generators, ExternalModules, and Primitives.
    Creates an instance of the generator's parameter-class if keyword args were provided instead.
    If both were provided, fail.
    """

    if kwargs and arg is not Default:
        msg = f"Invalid call to {callee}: either provide a single {callee.Params} instance or keyword arguments, not both."
        raise RuntimeError(msg)

    if arg is not Default:
        # Already constructed. Return as-is.
        # Note type-checking for instances of `callee.Params` *is not* done here.
        return arg

    # Create an instance of the parameter-class as indicated by the `Params` property of the callee.
    return callee.Params(**kwargs)
