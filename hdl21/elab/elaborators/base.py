"""
# Base Elaborator
"""


# Std-Lib Imports
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

# PyPi Imports
from pydantic.dataclasses import dataclass

# Local imports
from ...module import Module, ExternalModuleCall
from ...instance import InstArray, Instance, InstanceBundle
from ...primitives import PrimitiveCall
from ...bundle import BundleInstance
from ...generator import GeneratorCall
from ...instantiable import Instantiable

from ..elaboratable import Elaboratable
from ..context import Context


# Union of entry-types in the elaboration stack
ElabStackEntry = Union[GeneratorCall, Module, Instance, InstArray, InstanceBundle]


class Elaborator:
    """
    # Base Elaborator Class

    Defines the hierarchy-traversing methods used by each "elaborator pass" sub-class.

    For most passes, elaborating a `Module` at a time is the primary activity.
    To offload the need for each sub-class to cache `Module` definitions,
    and to traverse their internal contents, the base class defines `elaborate_module_base`, which:
    * Checks for the module result being pre-cached
    * Pre-order traverses its instances, arrays, and bundle instances
    * Calls the per-pass `elaborate_module`
    * Adds the result to the `modules` cache.
    This requires that sub-classes also carefully audit when they call their own
    `elaborate_module` method. Generally, they should not, and should always call
    `elaborate_module_base` instead.
    """

    @classmethod
    def elaborate(cls, top: Elaboratable, ctx: Context) -> Module:
        """Elaboration entry-point. Elaborate the top-level object."""
        return cls(top, ctx).elaborate_top()

    def __init__(self, top: Elaboratable, ctx: Context):
        self.top = top
        self.ctx = ctx
        self.stack: List[ElabStackEntry] = list()
        self.modules: Dict[int, Module] = dict()

    def elaborate_top(self) -> Module:
        """Elaborate our top node"""
        if not isinstance(self.top, Module):
            self.fail(f"Invalid Top for Elaboration: {self.top} must be a Module")
        return self.elaborate_module_base(self.top)  # Note `_base` here!

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """Elaborate a GeneratorCall"""
        # Only the generator-elaborator can handle generator calls.
        # By default it generates errors for all other elaboration passes.
        self.fail(f"Invalid call to elaborate GeneratorCall by {self}")

    def elaborate_module_base(self, module: Module) -> Module:
        """Base-Case `Module` Elaboration

        For most passes, elaborating a `Module` at a time is the primary activity.
        To offload the need for each sub-class to cache `Module` definitions,
        and to traverse their internal contents, the base class defines `elaborate_module_base`, which:
        * Checks for the module result being pre-cached
        * Pre-order traverses its instances, arrays, and bundle instances
        * Calls the per-pass `elaborate_module`
        * Adds the result to the `modules` cache.
        This requires that sub-classes also carefully audit when they call their own
        `elaborate_module` method. Generally, they should not, and should always call
        `elaborate_module_base` instead.
        """

        if id(module) in self.modules:  # Check our cache
            return module  # Already done!

        if not module.name:
            msg = f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            self.fail(msg)

        self.stack.append(module)

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_array(arr)
        for bundle in module.bundles.values():
            self.elaborate_bundle_instance(bundle)

        # Run the pass-specific `elaborate_module`
        result = self.elaborate_module(module)

        # Store a reference to the now-elaborated Module in our cache, and return it
        self.modules[id(module)] = result
        self.stack.pop()
        return result

    def elaborate_module(self, module: Module) -> Module:
        """Elaborate a Module. Returns the Module unmodified by default."""
        return module

    def elaborate_external_module(self, call: ExternalModuleCall) -> ExternalModuleCall:
        """Elaborate an ExternalModuleCall. Returns the Call unmodified by default."""
        return call

    def elaborate_primitive_call(self, call: PrimitiveCall) -> PrimitiveCall:
        """Elaborate a PrimitiveCall. Returns the Call unmodified by default."""
        return call

    def elaborate_bundle_instance(self, inst: BundleInstance) -> BundleInstance:
        """Elaborate an BundleInstance"""
        # Annotate each BundleInstance so that its pre-elaboration `PortRef` magic is disabled.
        inst._elaborated = True
        return inst

    def elaborate_instance_array(self, array: InstArray) -> Instantiable:
        """Elaborate an InstArray"""
        self.stack.append(array)
        # Turn off `PortRef` magic
        array._elaborated = True
        # And visit the Instance's target
        rv = self.elaborate_instantiable(array._resolved)
        self.stack.pop()
        return rv

    def elaborate_instance(self, inst: Instance) -> Instantiable:
        """Elaborate a Module Instance."""
        # This version of `elaborate_instantiable` is the "post-generators" version used by *most* passes.
        # The Generator-elaborator is different, and overrides it.

        self.stack.append(inst)
        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        rv = self.elaborate_instantiable(inst._resolved)
        self.stack.pop()
        return rv

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        # This version of `elaborate_instantiable` is the "post-generators" version used by *most* passes.
        # The Generator-elaborator is different, and overrides it.
        if not of:
            self.fail(f"Error elaborating undefined Instance-target {of}")
        if isinstance(of, Module):
            return self.elaborate_module_base(of)  # Note `_base` here!
        if isinstance(of, PrimitiveCall):
            return self.elaborate_primitive_call(of)
        if isinstance(of, ExternalModuleCall):
            return self.elaborate_external_module(of)
        raise TypeError

    def flatname(
        self, segments: List[str], *, avoid: Optional[Dict] = None, maxlen: int = 511
    ) -> str:
        """Create a attribute-name merging string-list `segments`, while avoiding all keys in dictionary `avoid`.
        Commonly re-used while flattening  nested objects and while creating explicit attributes from implicit ones.
        Raises a `RunTimeError` if no such name can be found of length less than `maxlen`.
        The default max-length is 511 characters, a value representative of typical limits in target EDA formats."""

        if avoid is None:
            avoid = {}

        # The default format and result is of the form "seg0_seg1".
        # If that is in the avoid-keys, append underscores until it's not, or fails.
        name = "_".join(segments)
        while True:
            if len(name) > maxlen:
                msg = f"Could not generate a flattened name for {segments}: (trying {name})"
                self.fail(msg)
            if name not in avoid:  # Done!
                break
            name += "_"  # Collision; append underscore
        return name

    def fail(self, msg: str):
        """Error helper, adding stack and state info to an error"""

        lines = []
        for s in self.stack:
            # Format:  Module          MyModule
            line = "  " + type(s).__name__.ljust(14) + str(s.name).ljust(28)

            source_info = getattr(s, "_source_info", None)
            if (
                source_info is not None
            ):  # The entry has source/line info. Add it to the error line.

                filepath = source_info.filepath
                # For paths in the run-directory, print the (presumably shorter) relative-path only
                if filepath.is_relative_to(Path.cwd()):
                    filepath = filepath.relative_to(Path.cwd())
                else:  # Otherwise print the full absolute path
                    filepath = filepath.resolve()

                # Format: /path/to/file.py:123
                # Serves as a clickable link in popular IDEs.
                line += f"{str(filepath)}:{source_info.linenum}"

            line += "\n"
            lines.append(line)

        msg = "Elaboration Error at hierarchical path: \n" + "".join(lines) + msg
        # This also serves as a very helpful place for a debugger breakpoint.
        raise RuntimeError(msg)
