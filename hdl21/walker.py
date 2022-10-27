"""
# Hierachy Walker Module 
"""

# Std-Lib
from typing import List

# Local imports
from .elab import Elaboratables
from .module import Module
from .external_module import ExternalModuleCall
from .instance import Instance
from .primitives import PrimitiveCall
from .bundle import BundleInstance
from .generator import GeneratorCall


class HierarchyWalker:
    """
    # Hierarchical Walker

    Walks a hierarchical design tree.
    Designed to be used as a base-class for extensions such as process-specific instance-replacements.
    """

    def visit_elaboratables(self, src: Elaboratables) -> None:
        """Visit an `Elaboratables` object.
        Largely dispatches across the type-union of elaboratable objects."""

        if isinstance(src, Module):
            return self.visit_module(src)
        if isinstance(src, GeneratorCall):
            return self.visit_generator_call(src)
        if isinstance(src, List):
            for x in src:
                self.visit_elaboratables(x)
            return
        raise TypeError

    def visit_generator_call(self, call: GeneratorCall) -> None:
        """Visit a `GeneratorCall` object, primarily by visiting its resultant `Module`."""
        return self.visit_module(call.gen._resolved)  # FIXME! think we broke this one.

    def visit_module(self, module: Module) -> None:
        """Visit a `Module`.
        Primary method for most manipulations."""

        for inst in module.instances.values():
            self.visit_instance(inst)
        for inst in module.bundles.values():
            self.visit_bundle_instance(inst)

    def visit_external_module(self, call: ExternalModuleCall) -> None:
        return

    def visit_primitive_call(self, call: PrimitiveCall) -> None:
        return

    def visit_bundle_instance(self, inst: BundleInstance) -> None:
        return

    def visit_instance(self, inst: Instance) -> None:
        """Visit a hierarchical `Instance`."""

        if isinstance(inst.of, GeneratorCall):
            return self.visit_generator_call(call=inst.of)
        if isinstance(inst.of, Module):
            return self.visit_module(inst.of)
        if isinstance(inst.of, PrimitiveCall):
            return self.visit_primitive_call(inst.of)
        if isinstance(inst.of, ExternalModuleCall):
            return self.visit_external_module(inst.of)
        raise TypeError(f"Invalid Instance of {inst.of}")
