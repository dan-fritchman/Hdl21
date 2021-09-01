"""
# hdl21 Generators
"""

import inspect
import pickle
from dataclasses import field
from typing import Callable, Union, Any, Optional
from types import ModuleType
from pydantic.dataclasses import dataclass
from pydantic import ValidationError

# Local imports
from .module import Module
from .instance import calls_instantiate


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

    def __call__(self, arg: Any):
        """ Calls to Generators create GeneratorCall-objects
        to be expanded during elaboration. """
        return GeneratorCall(gen=self, arg=arg)

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
    result: Optional[Module] = field(init=False, default=None)

    def __post_init_post_parse__(self):
        """ Validate that our argument matches the Generator param-type """
        if not isinstance(self.arg, self.gen.Params):
            raise ValidationError

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
        raise RuntimeError(
            f"Invalid generator call signature for {f.__name__}: {args}. First argument must be a paramclass."
        )
    # Check the context argument, if the function uses one
    usecontext = False
    if len(args) > 1:  # Also requests the context
        if args[1].annotation is not Context:
            raise RuntimeError(
                f"Invalid generator call signature for {f.__name__}: {args}. Second argument (if provided) must be a Context."
            )
        usecontext = True
    # Validate the return type is `Module`
    rt = sig.return_annotation
    if rt is not Module:
        raise TypeError(
            f"Generator {f.__name__} must return (and must be annotated to return) a Module."
        )

    # Grab a reference to the Python-module defining the function
    # (For later name-unique-ifying)
    pymodule = inspect.getmodule(f)
    return Generator(
        func=f, paramtype=paramtype, usecontext=usecontext, pymodule=pymodule
    )
