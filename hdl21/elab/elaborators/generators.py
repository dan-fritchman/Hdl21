"""
# Generator Elaborator 
"""

# Local imports
from ...module import Module
from ...instance import InstArray, Instance
from ...generator import GeneratorCall, Default as GenDefault
from ...params import HasNoParams, _unique_name
from ...instantiable import Instantiable

# Import the base class
from .base import Elaborator, ElabStackEnum


class GeneratorElaborator(Elaborator):
    """ 
    # Generator Elaborator
    
    Walks a hierarchy from `top` calling Generators. 
    This pass generally needs to run first among elaboration passes, 
    or else often times, if `top` is a GeneratorCall, 
    all other passes really don't have anything to do. 
    
    This fact is embedded in a few places throughout `GeneratorElaborator` 
    and how it inherits behavior from the base `Elaborator`. 
    Most (probably all) other passes require there be no `GeneratorCall`s 
    remaining as they operate, and instead act on those Call's `result` properties. 
    For reuse, this fact is embedded into the base-class in a few places, 
    and `GeneratorElaborator`'s special-ish case is left to over-ride it. 
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator_calls = dict()  # GeneratorCalls to their (Module) results

    def elaborate_top(self):
        """ Elaborate our top node """
        if isinstance(self.top, Module):
            return self.elaborate_module_base(self.top)
        if isinstance(self.top, GeneratorCall):
            return self.elaborate_generator_call(self.top)
        msg = f"Invalid Elaboration top-level {self.top}, must be a Module or Generator"
        raise TypeError(msg)

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """ Elaborate Generator-function-call `call`. Returns the generated Module. """

        # First check out cache
        if call in self.generator_calls:  # Already done!
            # Give the `call` a reference to its result.
            # Note this *has not* necessarily already happened, as the `self.generator_calls` key may be an equally-valued (but distinct) `GeneratorCall`.
            result = self.generator_calls[call]
            call.result = result
            return result

        self.stack_push(ElabStackEnum.GENERATOR, call.gen.name)

        # Support the "no paramclass constructor" invocation.
        # Create an instance of the generator's parameter-class if keyword args were provided instead.
        # If both were provided, fail.
        if call.kwargs and call.arg is not GenDefault:
            msg = f"Invalid Generator Call {call}: either provide a single {call.gen.Params} instance or keyword arguments, not both."
            raise RuntimeError(msg)
        elif call.arg is GenDefault:
            # Create an instance of the generator's parameter-class
            call.arg = call.gen.Params(**call.kwargs)

        # After all that, check that the call has a valid instance of the generator's parameter-class
        if not isinstance(call.arg, call.gen.Params):
            msg = f"Invalid Generator Call {call}: {call.gen.Params} instance required, got {call.arg}"
            raise RuntimeError(msg)

        # The main event: Run the generator-function
        if call.gen.usecontext:
            m = call.gen.func(call.arg, self.ctx)
        else:
            m = call.gen.func(call.arg)

        # Type-check the result
        # Generators may return other (potentially nested) generator-calls; unwind any of them
        while isinstance(m, GeneratorCall):
            # Note this should hit Python's recursive stack-check if it doesn't terminate
            m = self.elaborate_generator_call(m)
        # Ultimately they've gotta resolve to Modules, or they fail.
        if not isinstance(m, Module):
            msg = f"Generator {call.gen.func.__name__} returned {type(m)}, must return Module."
            raise TypeError(msg)

        # Give the GeneratorCall a reference to its result, and store it in our local dict
        call.result = m
        self.generator_calls[call] = m

        # Create a unique name
        # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
        if m.name is None:
            m.name = call.gen.func.__name__

        # Then add a unique suffix per its parameter-values
        if not isinstance(call.arg, HasNoParams):
            m.name += "(" + _unique_name(call.arg) + ")"

        # Update the Module's `pymodule`, which generally at this point is `hdl21.generator`
        m._pymodule = call.gen.pymodule

        # And elaborate the module
        m = self.elaborate_module_base(m)  # Note the `_base` here!
        self.stack_pop()
        return m

    def elaborate_instance(self, inst: Instance) -> Instantiable:
        """ Elaborate a Module Instance. """
        # This version differs from `Elaborator` in operating on the *unresolved* attribute `inst.of`,
        # instead of the resolved version `inst._resolved`.

        self.stack_push(ElabStackEnum.INSTANCE, inst.name)
        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        rv = self.elaborate_instantiable(inst.of)
        self.stack_pop()
        return rv

    def elaborate_instance_array(self, arr: InstArray) -> Instantiable:
        """ Elaborate an Instance Array. """
        # This version differs from `Elaborator` in operating on the *unresolved* attribute `inst.of`,
        # instead of the resolved version `inst._resolved`.

        self.stack_push(ElabStackEnum.INSTANCE, arr.name)
        # Turn off `PortRef` magic
        arr._elaborated = True
        # And visit the Instance's target
        rv = self.elaborate_instantiable(arr.of)
        self.stack_pop()
        return rv

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        """ Elaborate an Instance target. Adds the capacity to call `GeneratorCall`s to the more-common base-case. """
        if isinstance(of, GeneratorCall):
            return self.elaborate_generator_call(call=of)
        return super().elaborate_instantiable(of)
