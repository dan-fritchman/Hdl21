"""
# hdl21 Generators
"""

import inspect
from typing import Callable, Any, Optional, Dict

# Local imports
from .params import HasNoParams, _unique_name
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

    def __init__(self, func: Callable, paramtype: type):
        self.func = func
        self.paramtype = paramtype
        self._source_info: Optional[SourceInfo] = source_info(get_pymodule=True)

    def __call__(self, arg: Any = Default, **kwargs: Dict) -> "GeneratorCall":
        """Calls to Generators create GeneratorCall-objects
        to be expanded during elaboration."""
        params = param_call(callee=self, arg=arg, **kwargs)
        # FIXME: this is kinda the change! Probably clean it up
        return run(GeneratorCall(gen=self, params=params))

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


@calls_instantiate
class GeneratorCall:
    """# Generator Call

    Combination of a `Generator` function-wrapper and its parameter object.
    Stores its result `Module` after execution in its `result` field."""

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
        # FIXME: probably just `name`?
        return f"GeneratorCall(gen={self.gen.name})"

    @property
    def name(self) -> str:
        name = self.gen.name
        if not isinstance(self.params, HasNoParams):
            # FIXME: probably make this general over other "empty" param-classes
            name += "(" + _unique_name(self.params) + ")"
        return name


def _err(f: Callable, error: str) -> None:
    # If anything went wrong, write a generic message plus a more specific one.
    msg = f"Invalid generator call signature for generator function `{f.__name__}`.\n"
    msg += f"Generators must be of the form `def GenFunc(params: Params) -> Module`, where `Params` is a `paramclass`. \n"
    msg += error
    raise RuntimeError(msg)


def generator(f: Callable) -> Generator:
    """Decorator for Generator Functions"""

    from .params import isparamclass

    if not callable(f):
        raise RuntimeError(f"Invalid `@generator` application to non-callable {f}")

    # Grab, parse, and validate its call-signature
    sig = inspect.signature(f)

    args = list(sig.parameters.values())
    if len(args) < 1:
        msg = f"`{f.__name__}()` must have an argument which is a `paramclass`."
        return _err(f, msg)
    if len(args) > 1:
        return _err(f, f"`{f.__name__}()` has too many arguments.")

    # Extract the parameters-argument type
    paramtype = args[0].annotation
    if not isparamclass(paramtype):
        return _err(f, f"First argument must be a paramclass, not `{paramtype}`.")

    # Validate the return type is `Module`
    rt = sig.return_annotation
    if rt is not Module:
        msg = f"`{f.__name__}()` must return (and must be annotated to return) a Module, not `{rt}`."
        return _err(f, msg)

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
    global THE_GENERATOR_CALL_CACHE

    cached_result = THE_GENERATOR_CALL_CACHE.get(call, None)
    if cached_result is not None:
        if call.result is not None and call.result is not cached_result:
            msg = f"GeneratorCall {call} has two different results: {call.result} and {cached_result}"
            fail(msg)
        call.result = cached_result
        return call.result

    # Add both the `Call` and `Generator` to our stack.
    # self.stack.append(call)
    # self.stack.append(call.gen)

    # Check that the call has a valid instance of the generator's parameter-class
    if not isinstance(call.params, call.gen.Params):
        msg = f"Invalid Generator Call {call}: {call.gen.Params} instance required, got {call.params}"
        fail(msg)

    # The main event: Run the generator-function
    m = call.gen.func(call.params)
    # try:
    #     m = call.gen.func(call.params)
    # except Exception as e:
    #     fail(f"{call.gen} raised an exception: \n{e}")

    if not isinstance(m, Module):
        fail(f"Generator {call.gen} returned {m}, must return `Module`.")

    # Give the result a reference back to the generating `Call`
    m._generated_by = call

    # FIXME delete
    # And elaborate the module
    # m = self.elaborate_module_base(m)  # Note the `_base` here!

    # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
    if m.name is None:
        m.name = call.gen.name

    # Then add a unique suffix per its parameter-values
    # Note this part may require that `m` has been through elaboration above!
    if not isinstance(call.params, HasNoParams):
        # FIXME: probably make this general over other "empty" param-classes
        m.name += "(" + _unique_name(call.params) + ")"

    # # Generators may return other (potentially nested) generator-calls; recursively unwind any of them
    # # Note this should hit Python's recursive stack-check if it doesn't terminate
    # elif isinstance(m, GeneratorCall):
    #     m._generated_by = call
    #     m: Module = self.elaborate_generator_call(m)

    # # Type-check the result.
    # # Ultimately they've gotta resolve to Modules, or they fail.
    # else:
    #     msg = f"Generator {call.gen.func.__name__} returned {type(m)}, must return Module."
    #     fail(msg)

    # Store the result in our cache, and on the Call.
    call.result = m
    THE_GENERATOR_CALL_CACHE[call] = m

    # Pop both the `Call` and `Generator` off the stack
    # self.stack.pop()
    # self.stack.pop()

    # And return the generated Module
    return m


# Cache GeneratorCalls to their (Module) results
# (Yes, GeneratorCalls can be hashed.)
THE_GENERATOR_CALL_CACHE: Dict[GeneratorCall, Module] = dict()
