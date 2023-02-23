"""
# hdl21 Generators
"""

import inspect
from typing import Callable, Any, Optional, Dict

# Local imports
from .default import Default
from .call import param_call
from .params import _unique_name
from .source_info import SourceInfo, source_info
from .module import Module
from .instance import calls_instantiate


class Generator:
    """
    # Generator Object

    Typically created by the `@hdl.generator` decorator.
    Stores a function-object and parameters-type, along with some auxiliary data.
    """

    def __init__(self, func: Callable, paramtype: type, usecontext: bool):
        self.func = func
        self.paramtype = paramtype
        self.usecontext = usecontext
        self._source_info: Optional[SourceInfo] = source_info(get_pymodule=True)

    def __call__(self, arg: Any = Default, **kwargs: Dict) -> "GeneratorCall":
        """Calls to Generators create GeneratorCall-objects
        to be expanded during elaboration."""
        params = param_call(callee=self, arg=arg, **kwargs)
        return GeneratorCall(gen=self, params=params)

    def __repr__(self) -> str:
        return f"Generator(name={self.name})"

    def __eq__(self, other) -> bool:
        # Identity is equality
        return id(self) == id(other)

    def __hash__(self) -> bool:
        # Identity is equality
        return hash(id(self))

    @property
    def name(self) -> str:
        """Generator Name
        Equal to its callable-function's name."""
        return self.func.__name__

    @property
    def Params(self) -> type:
        """Type-style alias for the parameter-type."""
        return self.paramtype


@calls_instantiate
class GeneratorCall:
    """Generator 'Bare Calls'
    Stored for expansion during elaboration.
    Only single-argument calls with `Params` are supported.
    Any application of a `Context` is done during elaboration."""

    def __init__(self, gen: Generator, params: Any):
        self.gen = gen
        self.params = params
        self.result: Optional[Module] = None
        self._source_info: Optional[SourceInfo] = source_info(get_pymodule=False)
        # The source/ parent `GeneratorCall`, for nested Generator calls
        self._generated_by: Optional["GeneratorCall"] = None

    def __eq__(self, other) -> bool:
        """Generator-Call equality requires:
        * *Identity* between generators, and
        * *Equality* between parameter-values."""
        return self.gen is other.gen and self.params == other.params

    def __hash__(self):
        """Generator-Call hashing, consistent with `__eq__` above, uses:
        * *Identity* of its generator, and
        * *Value* of its parameters.
        The two are joined for hashing as a two-element tuple."""
        return hash((id(self.gen), self.params))

    def __repr__(self) -> str:
        return f"GeneratorCall(gen={self.gen.name})"

    @property
    def name(self) -> str:
        return self.gen.name + "(" + _unique_name(self.params) + ")"


def generator(f: Callable) -> Generator:
    """Decorator for Generator Functions"""
    from .params import isparamclass
    from .elab import Context

    if not callable(f):
        raise RuntimeError(f"Invalid `@generator` application to non-callable {f}")

    # Grab, parse, and validate its call-signature
    sig = inspect.signature(f)
    error: Optional[str] = None

    args = list(sig.parameters.values())
    if len(args) < 1:
        msg = f"`{f.__name__}()` must have an argument which is a `paramclass`."
        return _err(f, msg)
    if len(args) > 2:
        return _err(f, f"`{f.__name__}()` has too many arguments.")

    # Extract the parameters-argument type
    paramtype = args[0].annotation
    if not isparamclass(paramtype):
        return _err(f, f"First argument must be a paramclass, not `{paramtype}`.")

    # Check the context argument, if the function uses one
    usecontext = False
    if len(args) > 1:  # Also requests the context
        if args[1].annotation is not Context:
            msg = f"Second argument (if provided) must be a `Context`, not `{args[1].annotation}`."
            return _err(f, msg)
        usecontext = True

    # Validate the return type is `Module`
    rt = sig.return_annotation
    if rt is not Module:
        msg = f"`{f.__name__}()` must return (and must be annotated to return) a Module, not `{rt}`."
        return _err(f, msg)

    # And return the `Generator` object
    return Generator(func=f, paramtype=paramtype, usecontext=usecontext)


def _err(f: Callable, error: str) -> None:
    # If anything went wrong, write a generic message plus a more specific one.
    msg = f"Invalid generator call signature for generator function `{f.__name__}`.\n"
    msg += f"Generators must be of the form `def GenFunc(params: Params) -> Module`, where `Params` is a `paramclass`. \n"
    msg += error
    raise RuntimeError(msg)
