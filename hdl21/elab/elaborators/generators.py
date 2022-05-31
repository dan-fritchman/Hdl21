"""
# Generator Elaborator 
"""

# Std-Lib Imports
import copy
from typing import Union, Any, Dict, List, Optional, Tuple

# PyPi
from pydantic.dataclasses import dataclass

# Local imports
from ...connect import connectable
from ...module import Module, ExternalModuleCall
from ...instance import InstArray, Instance, PortRef
from ...primitives import PrimitiveCall
from ...bundle import AnonymousBundle, Bundle, BundleInstance, _check_compatible
from ...signal import PortDir, Signal, Visibility, Slice, Concat, Sliceable, NoConn
from ...generator import Generator, GeneratorCall, Default as GenDefault
from ...params import _unique_name
from ...instantiable import Instantiable

# Import the base class
from .base import _Elaborator


class GeneratorElaborator(_Elaborator):
    """ Hierarchical Generator Elaborator
    Walks a hierarchy from `top` calling Generators. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator_calls = dict()  # GeneratorCalls to their (Module) results
        self.modules = dict()  # Module ids to references
        self.primitive_calls = dict()  # PrimitiveCall ids to references
        self.ext_module_calls = dict()  # PrimitiveCall ids to references

    def elaborate_top(self):
        """ Elaborate our top node """
        if isinstance(self.top, Module):
            return self.elaborate_module(self.top)
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
        m.name += "(" + _unique_name(call.arg) + ")"
        # Update the Module's `pymodule`, which generally at this point is `hdl21.generator`
        m._pymodule = call.gen.pymodule
        # And elaborate the module
        return self.elaborate_module(m)

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. 
        Primarily performs flattening of Instance Arrays, 
        and re-connecting to the resultant flattened instances  """
        if id(module) in self.modules:  # Already done!
            return module

        if not module.name:
            msg = f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            raise RuntimeError(msg)

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_array(arr)
        # Also visit bundle instances, turning off their pre-elab magic
        for bundle in module.bundles.values():
            self.elaborate_bundle_instance(bundle)

        # Store a reference to the now-expanded Module in our cache, and return it
        self.modules[id(module)] = module
        return module

    def elaborate_instance(self, inst: Instance) -> Instantiable:
        """ Elaborate a Module Instance. """
        # This version differs from `Elaborator` in operating on the *unresolved* attribute `inst.of`,
        # instead of the resolved version `inst._resolved`.

        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(inst.of)

    def elaborate_instance_array(self, arr: InstArray) -> Instantiable:
        """ Elaborate an Instance Array. """
        # This version differs from `Elaborator` in operating on the *unresolved* attribute `inst.of`,
        # instead of the resolved version `inst._resolved`.

        # Turn off `PortRef` magic
        arr._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(arr.of)

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        """ Elaborate an Instance target. Adds the capacity to call `GeneratorCall`s to the more-common base-case. """
        if isinstance(of, GeneratorCall):
            return self.elaborate_generator_call(call=of)
        return super().elaborate_instantiable(of)
