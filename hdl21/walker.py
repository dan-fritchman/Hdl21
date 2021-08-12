"""
# Hierachy Walker Module 
"""

# Std-Lib
from types import SimpleNamespace

# Local imports
from .module import Module, ExternalModuleCall
from .instance import Instance
from .primitives import PrimitiveCall
from .interface import Interface, InterfaceInstance
from .signal import Port, PortDir, Signal, Visibility
from .generator import Generator, GeneratorCall


class HierarchyWalker:
    """Hierarchical Traversal Helper
    Walks a hierarchical `Module` or `SimpleNamespace` thereof.
    Designed to be used as a base-class for extensions such as
    process-specific instance-replacements."""

    def visit_namespace(self, ns: SimpleNamespace):
        for k, v in ns.__dict__.items():
            if isinstance(v, Module):
                self.visit_module(v)
            if isinstance(v, SimpleNamespace):
                self.visit_namespace(v)

    def visit_generator_call(self, call: GeneratorCall):
        raise NotImplementedError

    def visit_module(self, module: Module):
        for inst in module.instances.values():
            self.visit_instance(inst)
        for inst in module.interfaces.values():
            self.visit_interface_instance(inst)

    def visit_external_module(self, call: ExternalModuleCall):
        return

    def visit_primitive_call(self, call: PrimitiveCall):
        return

    def visit_interface_instance(self, inst: InterfaceInstance):
        return

    def visit_instance(self, inst: Instance):
        if isinstance(inst.of, GeneratorCall):
            return self.visit_generator_call(call=inst.of)
        if isinstance(inst.of, Module):
            return self.visit_module(inst.of)
        if isinstance(inst.of, PrimitiveCall):
            return self.visit_primitive_call(inst.of)
        if isinstance(inst.of, ExternalModuleCall):
            return self.visit_external_module(inst.of)
        raise TypeError(f"Invalid Instance of {inst.of}")
