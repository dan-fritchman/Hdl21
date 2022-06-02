"""
# hdl21 Generators
"""

import inspect
import pickle
from dataclasses import field
from typing import Callable, Any, Optional, Dict
from types import ModuleType
from pydantic.dataclasses import dataclass
from pydantic import ValidationError

# Local imports
from .module import Module
from .instance import calls_instantiate


@dataclass
class Default:
    """ Default value for generator arguments """

    ...  # Empty contents


@dataclass
class Generator:
    """ # Generator Object 
    Typically created by the `@hdl.generator` decorator. 
    Stores a function-object and parameters-type, 
    along with some auxiliary data. 
    """

    func: Callable  # The generator function
    paramtype: type  # Parameter type
    usecontext: bool  # Boolean indication of `Context` usage
    pymodule: ModuleType  # Python module where function defined

    def __call__(self, arg: Any = Default, **kwargs) -> "GeneratorCall":
        """ Calls to Generators create GeneratorCall-objects
        to be expanded during elaboration. """
        return GeneratorCall(gen=self, arg=arg, kwargs=kwargs)

    @property
    def name(self) -> str:
        """ Generator Name
        Equal to its callable-function's name. """
        return self.func.__name__

    @property
    def Params(self) -> type:
        """ Parameter-Type Property """
        return self.paramtype


@calls_instantiate
@dataclass
class GeneratorCall:
    """ Generator 'Bare Calls' 
    Stored for expansion during elaboration. 
    Only single-argument calls with `Params` are supported. 
    Any application of a `Context` is done during elaboration.  """

    gen: Generator
    arg: Any
    kwargs: Dict[str, Any]
    result: Optional[Module] = field(init=False, default=None)

    def __eq__(self, other) -> bool:
        """ Generator-Call equality requires:
        * *Identity* between generators, and 
        * *Equality* between parameter-values. """
        return self.gen is other.gen and self.arg == other.arg

    def __hash__(self):
        """ Generator-Call hashing, consistent with `__eq__` above, uses:
        * *Identity* of its generator, and 
        * *Value* of its parameters. 
        The two are joined for hashing as a two-element tuple. """
        return hash((id(self.gen), pickle.dumps(self.arg)))

    @property
    def name(self) -> str:
        """ GeneratorCall Naming 
        Once elaborated, returns the name of the generated Module. 
        If not elaborated, raises a `RuntimeError`. """
        if self.result is None:
            raise RuntimeError(f"Cannot name un-elaborated GeneratorCall {self}")
        return self.result.name


def generator(f: Callable) -> Generator:
    """ Decorator for Generator Functions """
    from .params import isparamclass
    from .elab import Context

    if not callable(f):
        raise RuntimeError(f"Invalid `@generator` application to non-callable {f}")

    # Grab, parse, and validate its call-signature
    sig = inspect.signature(f)

    args = list(sig.parameters.values())
    if len(args) < 1 or len(args) > 2:
        raise RuntimeError(f"Invalid generator call signature for {f.__name__}: {args}")

    # Extract the parameters-argument type
    paramtype = args[0].annotation
    if not isparamclass(paramtype):
        msg = f"Invalid generator call signature for {f.__name__}: {args}. First argument must be a paramclass."
        raise RuntimeError(msg)

    # Check the context argument, if the function uses one
    usecontext = False
    if len(args) > 1:  # Also requests the context
        if args[1].annotation is not Context:
            msg = f"Invalid generator call signature for {f.__name__}: {args}. Second argument (if provided) must be a Context."
            raise RuntimeError(msg)
        usecontext = True

    # Validate the return type is `Module`
    rt = sig.return_annotation
    if rt is not Module:
        msg = f"Generator {f.__name__} must return (and must be annotated to return) a Module."
        raise TypeError(msg)

    # Grab a reference to the Python-module defining the function
    # (For later name-unique-ifying)
    pymodule = inspect.getmodule(f)
    return Generator(
        func=f, paramtype=paramtype, usecontext=usecontext, pymodule=pymodule
    )
