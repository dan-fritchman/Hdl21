import inspect
from typing import Callable, Union, Any
from pydantic.dataclasses import dataclass
from pydantic import ValidationError
from .module import Module


class Context:
    ...


@dataclass
class Generator:
    func: Callable
    paramtype: type
    usecontext: bool

    def __call__(self, arg: Any):
        return GeneratorCall(gen=self, arg=arg)

    @property
    def Params(self) -> type:
        return self.paramtype


@dataclass
class GeneratorCall:
    """ Generator 'Bare Calls' 
    Stored for expansion during elaboration. 
    Only single-argument calls with `Params` are supported. 
    Any application of a `Context` is done during elaboration.  """

    gen: Generator
    arg: Any

    def __post_init_post_parse__(self):
        if not isinstance(self.arg, self.gen.Params):
            raise ValidationError


def generator(f: Callable) -> Generator:
    """ Decorator for Generator Functions """
    from .params import isparamclass

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
    return Generator(func=f, paramtype=paramtype, usecontext=usecontext)


class Elaborator:
    def __init__(
        self, *, top: Union[Module, Generator], params: object, ctx: Context,
    ):
        self.top = top
        self.ctx = ctx
        self.params = params
        # Keep the defined Modules in two collections, an ordered list and a set for quick membership tests
        self.module_order = list()
        self.module_set = set()

    def elaborate(self):
        """ Elaborate our top node """
        if isinstance(self.top, Module):
            return self.elaborate_module(self.top)
        if isinstance(self.top, Generator):
            return self.elaborate_generator(self.top, self.params)
        raise TypeError(
            f"Invalid Elaboration top-level {self.top}, must be a Module or Generator"
        )

    def elaborate_generator(self, gen: Generator, params: object) -> Module:
        """ Elaborate Generator-function `gen` with Parameters `params`. 
        Returns the generated Module. """

        # The main event: Run the generator-function
        if gen.usecontext:
            m = gen.func(params, self.ctx)
        else:
            m = gen.func(params)

        # Type-check the result
        # Generators may return other (potentially nested) generator-calls; unwind any of them
        while isinstance(m, GeneratorCall):
            # Note this should hit Python's recursive stack-check if it doesn't terminate
            m = self.elaborate_generator(gen=m.gen, params=m.arg)
        # Ultimately they've gotta resolve to Modules, or they fail.
        if not isinstance(m, Module):
            raise TypeError(
                f"Generator {self.func.__name__} returned {type(m)}, must return Module."
            )

        # Give it a reference to its generator-parameters
        m._genparams = params
        # If the Module that comes back is anonymous, give it a name equal to the Generator's
        if m.name is None:
            m.name = gen.func.__name__
        # And elaborate the module
        return self.elaborate_module(m)

    def elaborate_module(self, module: Module) -> Module:
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        return module

    def elaborate_instance(self, inst: "Instance"):
        if isinstance(inst.of, Generator):
            return self.elaborate_generator(inst.of, inst.params)
        if isinstance(inst.of, GeneratorCall):
            return self.elaborate_generator(gen=inst.of.gen, params=inst.of.arg)
        if isinstance(inst.of, Module):
            return self.elaborate_module(inst.of)
        raise TypeError(f"Invalid Instance of {inst.of}")


def elaborate(top: Generator, params=None, ctx=None):
    """ In-Memory Elaborate Generator or Module `top`. """
    ctx = ctx or Context()
    if params is not None and not isinstance(top, Generator):
        raise RuntimeError(
            f"Error attempting to elaborate non-generator {top} with non-null params {params}"
        )
    elab = Elaborator(top=top, params=params, ctx=ctx)
    return elab.elaborate()

