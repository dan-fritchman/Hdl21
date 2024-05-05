"""
# Generators

Functions that return Modules. 
Including facilities for embedding them in a hardware hierarchy. 
"""

# Std-Lib imports
import inspect
from dataclasses import field
from typing import Callable, Any, Optional, Dict, Set, List, Type

# Local imports
from .datatype import datatype, AllowArbConfig
from .params import _unique_name, hasparams, isparamclass
from .default import Default
from .call import param_call
from .source_info import SourceInfo, source_info
from .module import Module


@datatype
class Generator:
    """
    # Generator Object

    Typically created by the `@hdl.generator` decorator.
    Stores a function-object and parameters-type, along with some auxiliary data.
    """

    func: Callable[[Any], Module]
    paramtype: Type[object]

    # Optional fields
    # Boolean indication of whether to cache calls, or return a new Module with each call.
    enable_cache: bool = True

    def __post_init__(self):
        if not isparamclass(self.paramtype):
            raise TypeError(
                f"Invalid paramtype {self.paramtype} for Generator {self.func}"
            )
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


def validate(f: Callable, **kwargs: Dict) -> Generator:
    """# Validate function `f` to be a `Generator`."""

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
    return Generator(func=f, paramtype=paramtype, **kwargs)


def generator(f: Optional[Callable] = None, **kwargs: Dict) -> Generator:
    """Decorator for Generator Functions"""

    # Accept either with or without parenthetical modifier arguments.
    inner = lambda func: validate(func, **kwargs)
    if f is None:
        return inner  # Called with parentheses
    return inner(f)  # Called without parentheses


@datatype
class GeneratorCall:
    """
    # Generator Call

    Combination of a `Generator` function-wrapper and its parameters.
    Serves as the key in the `GeneratorCache`.
    """

    gen: Generator
    params: Any

    def __eq__(self, other) -> bool:
        """
        # Generator-Call Equality
        Requires:
        - *Identity* between generators, and
        - *Equality* between parameter-values.
        """
        return self.gen is other.gen and self.params == other.params

    def __hash__(self):
        """
        # Generator-Call Hashing
        Consistent with `__eq__` above, uses:
        - *Identity* of its generator, and
        - *Value* of its parameters.
        The two are joined for hashing as a two-element tuple.
        """
        return hash((id(self.gen), self.params))


def run(call: GeneratorCall) -> Module:
    """Run Generator-function-call `call`. Returns the generated Module."""

    # First and foremost - caching.
    # See if we've already run this generator-parameters combo.
    the_cache = Generator.Cache
    if call.gen.enable_cache:
        cached_result = the_cache.done.get(call, None)
        if cached_result is not None:
            return cached_result

    # Add to the call stack.
    # This is helpful even if (especially if) we find it's a circular dependency next.
    the_cache.stack.append(call)

    if call.gen.enable_cache:
        # Check for circular dependencies.
        # Note this uses a hash-set of `GeneratorCall`s, so only hashable ones get checked.
        if call in the_cache.pending:
            msg = f"Invalid self referencing/ circular dependency in `{call}`"
            raise RuntimeError(msg)
        the_cache.pending.add(call)

    # Check that the call has a valid instance of the generator's parameter-class
    if not isinstance(call.params, call.gen.Params):
        msg = f"Invalid Generator Call {call}: {call.gen.Params} instance required, got {call.params}"
        raise RuntimeError(msg)

    # The main event: Run the generator-function
    m = call.gen.func(call.params)

    if not isinstance(m, Module):
        msg = f"Generator {call.gen} returned {m}, must return `Module`."
        raise RuntimeError(msg)

    # Give the result a reference back to the generating `Call`
    m._generated_by = call

    # Module naming
    # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
    if m.name is None:
        m.name = call.gen.name

    # If it has a nonzero number of parameters, add a unique suffix per its parameter-values
    if hasparams(call.gen.Params):
        m.name += "(" + _unique_name(call.params) + ")"

    # Store the result in our cache, and on the Call.
    the_cache.stack.pop()
    if call.gen.enable_cache:
        the_cache.pending.remove(call)
        the_cache.done[call] = m

    # And return the generated Module
    return m


@datatype(config=AllowArbConfig)
class GeneratorCache:
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
        """# Reset
        Clear everything in the Generator cache."""
        self.done.clear()
        self.pending.clear()
        self.stack.clear()


# Create the `Cache`, and affix it to the `generator` function and class
generator.cache = Generator.Cache = GeneratorCache()

# Star-exports
__all__ = ["Generator", "generator"]
