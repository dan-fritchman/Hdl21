"""
# Param-Class Argument Calls

Enables the "no paramclass constructor" style invocation for Generators, ExternalModules, and Primitives.
Creates an instance of the generator's parameter-class if keyword args were provided instead.
If both were provided, fail.
"""

from typing import Union, Any, Dict
from pydantic import ValidationError

# Local Imports
from .default import Default


# Union of types designed to support `param_call`,
# which more specifically must have a `Params` property, which is a type.
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

    try:
        # Try to create and return an instance of the parameter-class
        # As indicated by the `Params` property of the callee.
        return callee.Params(**kwargs)

    except (TypeError, ValidationError) as e:
        # Type validation failed; add some of our info to the error message.

        # A very common case is forgetting to apply parameters, and going straight to connections.
        # Check for this, and provide a specific error message when it happens.
        from .connect import is_connectable

        connectables = [key for key, val in kwargs.items() if is_connectable(val)]
        if connectables:
            msg = f"Invalid call to {callee} with connectables: ({', '.join(connectables)}). \n"
            msg += f"Did you forget to pass this its `params` ({callee.Params.__name__}) first?"
            raise RuntimeError(msg)

        # FIXME: add `SourceInfo`
        msg = f"Invalid call to `{callee}` with arguments `{kwargs}`: \n\n{e}"
        raise RuntimeError(msg)

    except:  # Any other Exception, raise along
        raise
