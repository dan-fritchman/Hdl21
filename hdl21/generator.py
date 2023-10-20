"""
# Generators

Functions that return Modules. 
Including facilities for embedding them in a hardware hierarchy. 
"""

# Std-Lib imports
import inspect
from dataclasses import field
from typing import Callable, Any, Optional, Dict, Set, List

# PyPi imports
from pydantic.dataclasses import dataclass

# Local imports
from .params import _unique_name, hasparams, isparamclass
from .default import Default
from .call import param_call
from .source_info import SourceInfo, source_info
from .module import Module


class Generator:
    """
    # Generator Object

    Typically created by the `@hdl.generator` decorator.
    Stores a function-object and parameters-type, along with some auxiliary data.
    """

    def __init__(self, func: Callable, paramtype: type):
        self.func = func
        if not isparamclass(paramtype):
            raise TypeError(f"Invalid paramtype {paramtype} for Generator {func}")
        self.paramtype = paramtype
        self._source_info: Optional[SourceInfo] = source_info(get_pymodule=True)

    def __call__(self, arg: Any = Default, **kwargs: Dict) -> Module:
        params = param_call(callee=self, arg=arg, **kwargs)
        call = GeneratorCall(gen=self, params=params)
        return run(call)

    def __repr__(self) -> str:
        return f"Generator(name={self.name})"

    def __eq__(self, other) -> bool:
        # Identity is equality
        return other is self

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


class GeneratorCall:
    """
    # Generator Call

    Combination of a `Generator` function-wrapper and its parameter object.
    Stores its result `Module` after execution in its `result` field.

    Note that while `GeneratorCall`s are techinically mutated by that process,
    we still hash, compare, and cache them based on their *generator identity* and *parameter values*.
    """

    def __init__(self, gen: Generator, params: Any):
        self.gen = gen
        self.params = params
        self.result: Optional[Module] = None
        self._source_info: Optional[SourceInfo] = source_info(get_pymodule=False)

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
        return f"GeneratorCall(name={self.name})"

    @property
    def name(self) -> str:
        name = self.gen.name
        if hasparams(self.gen.Params):
            name += "(" + _unique_name(self.params) + ")"
        return name


def generator(f: Callable) -> Generator:
    """Decorator for Generator Functions"""

    def invalid(s: str) -> RuntimeError:
        # If anything went wrong, write a generic message plus a more specific one.
        msg = f"Invalid call signature for generator function `{f.__name__}`.\n"
        msg += f"Generators must be of the form `def GenFunc(params: Params) -> Module`, where `Params` is a `paramclass`. \n"
        msg += s
        return RuntimeError(msg)

    if not callable(f):
        raise RuntimeError(f"Invalid `@generator` application to non-callable {f}")

    # Grab, parse, and validate its call-signature
    sig = inspect.signature(f)

    args = list(sig.parameters.values())
    if len(args) != 1:
        msg = f"Generator `{f.__name__}()` must have a single argument which is a `paramclass`."
        raise invalid(msg)

    # Extract the parameters-argument type
    paramtype = args[0].annotation
    if not isparamclass(paramtype):
        msg = f"First argument must be a paramclass, not `{paramtype}`."
        raise invalid(msg)

    # Validate the return type is `Module`
    rt = sig.return_annotation
    if rt is not Module:
        msg = f"`{f.__name__}()` must return (and must be annotated to return) a Module, not `{rt}`."
        raise invalid(msg)

    # And return the `Generator` object
    return Generator(func=f, paramtype=paramtype)


def fail(msg: str):
    raise RuntimeError(msg)


def run(call: GeneratorCall) -> Module:
    """Run Generator-function-call `call`. Returns the generated Module."""

    # First and foremost - caching.
    # See if we've already run this generator-parameters combo.
    # We store this both in the module-scope cache, and on the Call itself.
    # If the two are different Modules... not sure what would cause that, but fail.
    cache = Generator.Cache
    cached_result = cache.done.get(call, None)
    if cached_result is not None:
        if call.result is not None and call.result is not cached_result:
            msg = f"GeneratorCall {call} has two different results: {call.result} and {cached_result}"
            fail(msg)
        call.result = cached_result
        return call.result

    # Add to the call stack.
    # This is helpful even if (especially if) we find it's a circular dependency next.
    cache.stack.append(call)

    # Check for circular dependencies
    if call in cache.pending:
        msg = f"Invalid self referencing/ circular dependency in `{call}`"
        return fail(msg)
    cache.pending.add(call)

    # Check that the call has a valid instance of the generator's parameter-class
    if not isinstance(call.params, call.gen.Params):
        msg = f"Invalid Generator Call {call}: {call.gen.Params} instance required, got {call.params}"
        fail(msg)

    # The main event: Run the generator-function
    m = call.gen.func(call.params)

    if not isinstance(m, Module):
        fail(f"Generator {call.gen} returned {m}, must return `Module`.")

    # Give the result a reference back to the generating `Call`
    m._generated_by = call

    # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
    if m.name is None:
        m.name = call.gen.name

    # If it has a nonzero number of parameters, add a unique suffix per its parameter-values
    if hasparams(call.gen.Params):
        m.name += "(" + _unique_name(call.params) + ")"

    # Store the result in our cache, and on the Call.
    call.result = m
    cache.stack.pop()
    cache.done[call] = m
    cache.pending.remove(call)

    # And return the generated Module
    return m


@dataclass
class Cache:
    """
    # Generator "Cache" (and then some)

    - Cache GeneratorCalls to their (Module) results
      - (Yes, GeneratorCalls can be hashed.)
    - Track pending and completed GeneratorCalls
    """

    done: Dict[GeneratorCall, Module] = field(default_factory=dict)
    pending: Set[GeneratorCall] = field(default_factory=set)
    stack: List[GeneratorCall] = field(default_factory=list)

    def reset(self):
        self.done.clear()
        self.pending.clear()
        self.stack.clear()


# Create the `Cache`
generator.cache = Generator.Cache = Cache()

# Star-exports
# FIXME: make `GeneratorCall` "private"
__all__ = ["Generator", "generator", "GeneratorCall"]
