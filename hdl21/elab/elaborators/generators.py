"""
# Generator Elaborator 
"""

from typing import List, Dict, Union

# Local imports
from ...module import Module
from ...instance import Instance
from ...generator import GeneratorCall
from ...params import HasNoParams, _unique_name
from ...instantiable import Instantiable

# Import the base class
from .base import Elaborator


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
        # Cache GeneratorCalls to their (Module) results
        # (Yes, GeneratorCalls can be hashed.)
        self.generator_calls: Dict[GeneratorCall, Module] = dict()

    def elaborate_tops(self) -> List[Module]:
        """Elaborate our top nodes"""
        if not isinstance(self.tops, List):
            self.fail(f"Invalid Top for Elaboration: {self.tops} must be a list")
        return [self.elaborate_a_top_node(t) for t in self.tops]

    def elaborate_a_top_node(self, t: Union[Module, GeneratorCall]) -> Module:
        """Elaborate a top-level node, which may be a Module or a GeneratorCall."""
        if isinstance(t, Module):
            return self.elaborate_module_base(t)  # Note `_base` here!

        if isinstance(t, GeneratorCall):
            return self.elaborate_generator_call(t)

        self.fail(
            f"Invalid Elaboration top-level {t}, must be a Module or call to Generator"
        )

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """Elaborate Generator-function-call `call`. Returns the generated Module."""

        # First and foremost - caching.
        # See if we've already run this generator-parameters combo.
        # There are two places its result could be cached:
        # (a) In our cache, if we've already run it or a parameter-equal call to it. Or,
        # (b) On the `call`, on its `result` field - if a *different elaborator* has already run it.
        # If there's a Module in both places, and the aren't the same Module... not sure what happened. Fail.
        cached_result = self.generator_calls.get(call, None)
        if call.result is not None and cached_result is not None:
            if call.result is not cached_result:
                msg = f"GeneratorCall {call} has two different results: {call.result} and {cached_result}"
                self.fail(msg)
        if call.result is not None:
            self.generator_calls[call] = call.result
            return call.result
        if cached_result is not None:
            call.result = cached_result
            return call.result

        # Add both the `Call` and `Generator` to our stack.
        self.stack.append(call)
        self.stack.append(call.gen)

        # Check that the call has a valid instance of the generator's parameter-class
        if not isinstance(call.params, call.gen.Params):
            msg = f"Invalid Generator Call {call}: {call.gen.Params} instance required, got {call.params}"
            self.fail(msg)

        # The main event: Run the generator-function
        try:
            if call.gen.usecontext:
                m = call.gen.func(call.params, self.ctx)
            else:
                m = call.gen.func(call.params)
        except Exception as e:
            self.fail(f"{call.gen} raised an exception: \n{e}")

        # Type-check the result
        # Generators may return other (potentially nested) generator-calls; unwind any of them
        while isinstance(m, GeneratorCall):
            # Note this should hit Python's recursive stack-check if it doesn't terminate
            m = self.elaborate_generator_call(m)
        # Ultimately they've gotta resolve to Modules, or they fail.
        if not isinstance(m, Module):
            msg = f"Generator {call.gen.func.__name__} returned {type(m)}, must return Module."
            self.fail(msg)

        # Give the GeneratorCall a reference to its result, and store it in our local dict
        call.result = m
        self.generator_calls[call] = m

        # Create a unique name
        # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
        if m.name is None:
            m.name = call.gen.func.__name__

        # Then add a unique suffix per its parameter-values
        if not isinstance(call.params, HasNoParams):
            m.name += "(" + _unique_name(call.params) + ")"

        # And elaborate the module
        m = self.elaborate_module_base(m)  # Note the `_base` here!

        # Pop both the `Call` and `Generator` off the stack
        self.stack.pop()
        self.stack.pop()

        # And return the generated Module
        return m

    def elaborate_instance_base(self, inst: Instance) -> Instantiable:
        """Elaborate a Module Instance."""
        # This version differs from `Elaborator` in operating on the *unresolved* attribute `inst.of`,
        # instead of the resolved version `inst._resolved`.

        self.stack.append(inst)
        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        rv = self.elaborate_instantiable(inst.of)
        self.stack.pop()
        return rv

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        """Elaborate an Instance target. Adds the capacity to call `GeneratorCall`s to the more-common base-case."""
        if isinstance(of, GeneratorCall):
            return self.elaborate_generator_call(call=of)
        return super().elaborate_instantiable(of)
