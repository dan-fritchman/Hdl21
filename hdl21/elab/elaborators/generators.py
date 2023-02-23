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


# Cache GeneratorCalls to their (Module) results
# (Yes, GeneratorCalls can be hashed.)
THE_GENERATOR_CALL_CACHE: Dict[GeneratorCall, Module] = dict()


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
        # We store this both in the module-scope cache, and on the Call itself.
        # If the two are different Modules... not sure what would cause that, but fail.
        global THE_GENERATOR_CALL_CACHE
        cached_result = THE_GENERATOR_CALL_CACHE.get(call, None)
        if cached_result is not None:
            if call.result is not None and call.result is not cached_result:
                msg = f"GeneratorCall {call} has two different results: {call.result} and {cached_result}"
                self.fail(msg)
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

        if isinstance(m, Module):
            # Give the result a reference back to the generating `Call`
            m._generated_by = call

            # And elaborate the module
            m = self.elaborate_module_base(m)  # Note the `_base` here!

            # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
            if m.name is None:
                m.name = call.gen.func.__name__

            # Then add a unique suffix per its parameter-values
            # Note this part may require that `m` has been through elaboration above!
            if not isinstance(call.params, HasNoParams):
                m.name += "(" + _unique_name(call.params) + ")"

        # Generators may return other (potentially nested) generator-calls; recursively unwind any of them
        # Note this should hit Python's recursive stack-check if it doesn't terminate
        elif isinstance(m, GeneratorCall):
            m._generated_by = call
            m: Module = self.elaborate_generator_call(m)

        # Type-check the result.
        # Ultimately they've gotta resolve to Modules, or they fail.
        else:
            msg = f"Generator {call.gen.func.__name__} returned {type(m)}, must return Module."
            self.fail(msg)

        # Store the result in our cache, and on the Call.
        call.result = m
        THE_GENERATOR_CALL_CACHE[call] = m

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
