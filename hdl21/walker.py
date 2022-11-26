"""
# Hierachy Walker Module 
"""

# Std-Lib
from typing import List

# Local imports
from .elab import Elaboratable, Elaboratables, elaborate, is_elaboratable
from .instance import Instance
from .instantiable import Instantiable
from .module import Module
from .external_module import ExternalModuleCall
from .primitives import PrimitiveCall
from .generator import GeneratorCall


class HierarchyWalker:
    """
    # Hierarchical Walker

    Walks a hierarchical design tree.
    Designed to be used as a base-class for extensions such as process-specific instance-replacements.
    """

    def visit_elaboratables(self, src: Elaboratables) -> Elaboratables:
        """Visit an `Elaboratables` object.
        Largely dispatches across the type-union of elaboratable objects."""

        # First ensure all the `src` modules and generators are elaborated.
        # This is a functional no-op if they already are.
        elaborate(src)

        if isinstance(src, List):
            for x in src:
                self.visit_elaboratable(x)
            return src
        if is_elaboratable(src):
            return self.visit_elaboratable(src)
        raise TypeError(f"Cannot walk non-elaboratable {src}")

    def visit_elaboratable(self, src: Elaboratable) -> Elaboratable:
        """Visit an `Elaboratable` object."""

        if isinstance(src, Module):
            return self.visit_module(src)
        if isinstance(src, GeneratorCall):
            return self.visit_generator_call(src)
        raise TypeError(f"Cannot walk non-elaboratable {src}")

    def visit_module(self, module: Module) -> Instantiable:
        """Visit a `Module`.
        Primary method for most manipulations."""

        # Step into each of the Module's instances.
        # Note that as we have already elaborated, it no longer has bundles.
        for inst in module.instances.values():
            self.visit_instance(inst)
        return module

    def visit_generator_call(self, call: GeneratorCall) -> Instantiable:
        """Visit a `GeneratorCall` object, primarily by visiting its resultant `Module`."""
        if call.result is None:
            raise RuntimeError(f"Generator {call} has not been elaborated")
        call.result = self.visit_module(call.result)
        return call.result

    def visit_external_module_call(self, call: ExternalModuleCall) -> Instantiable:
        """Visit an `ExternalModuleCall`.
        A common place to perform "module replacement" in sub-classes.
        Base implementation does nothing."""
        return call

    def visit_primitive_call(self, call: PrimitiveCall) -> Instantiable:
        """Visit an `PrimitiveCall`.
        A common place to perform "module replacement" in sub-classes,
        especially when transforming Hdl21's generic `Primitive`s into technology-specific devices.
        Base implementation does nothing."""
        return call

    def visit_instance(self, inst: Instance) -> Instance:
        """Visit a hierarchical `Instance`.
        Visits and sets its `of` field to the result of `visit_instantiable`."""
        inst.of = self.visit_instantiable(inst.of)
        return inst

    def visit_instantiable(self, of: Instantiable) -> Instantiable:
        """Visit an `Instantiable` instance-target."""

        if isinstance(of, GeneratorCall):
            return self.visit_generator_call(call=of)
        if isinstance(of, Module):
            return self.visit_module(of)
        if isinstance(of, PrimitiveCall):
            return self.visit_primitive_call(of)
        if isinstance(of, ExternalModuleCall):
            return self.visit_external_module_call(of)
        raise TypeError(f"Invalid Instance of {of}")

    @classmethod
    def walk(cls, src: Elaboratables) -> Elaboratables:
        """Walk a hierarchical design tree or list of them.
        Class-level method commonly called on sub-classes, e.g. in PDK compilation methods."""
        return cls().visit_elaboratables(src)


def walk(src: Elaboratables) -> Elaboratables:
    """Walk a hierarchical design tree or list of them."""
    return HierarchyWalker.walk(src)
