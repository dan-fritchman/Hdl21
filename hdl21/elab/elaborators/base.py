"""
# Base Elaborator
"""


# Std-Lib Imports
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Local imports
from ...module import Module
from ...external_module import ExternalModuleCall
from ...instance import _Instance, Instance, InstanceArray, InstanceBundle
from ...primitives import PrimitiveCall
from ...bundle import BundleInstance
from ...generator import GeneratorCall
from ...instantiable import Instantiable

from ..elaboratable import Elaboratable
from ..context import Context


# Union of entry-types in the elaboration stack
ElabStackEntry = Union[GeneratorCall, Module, Instance, InstanceArray, InstanceBundle]


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
    def elaborate(cls, tops: List[Elaboratable], ctx: Context) -> List[Elaboratable]:
        """Elaboration entry-point. Elaborate the top-level objects."""
        return cls(tops, ctx).elaborate_tops()

    def __init__(self, tops: List[Elaboratable], ctx: Context):
        self.tops = tops
        self.ctx = ctx
        self.stack: List[ElabStackEntry] = list()

    def elaborate_tops(self) -> List[Elaboratable]:
        """Elaborate our top nodes"""
        if not isinstance(self.tops, List):
            self.fail(f"Invalid Top for Elaboration: {self.tops} must be a list")

        # The base-class Elaborator, and most sub-classes, return the `self.tops` list unmodified,
        # while modifiying its elements inline.
        # This differs from the `Generator` elaborator, which returns a new list,
        # generally converting `GeneratorCall`s into `Module`s.

        for t in self.tops:
            self.elaborate_module_base(t)  # Note `_base` here!
        return self.tops

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

        # Check if this has already been elaborated
        if module._elaborated is not None:
            return module._elaborated

        self.stack.append(module)

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance_base(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_base(arr)
        for instbundle in module.instbundles.values():
            self.elaborate_instance_base(instbundle)

        # Traverse Bundle instances
        for bundle in module.bundles.values():
            self.elaborate_bundle_instance(bundle)

        # Run the pass-specific `elaborate_module`
        result = self.elaborate_module(module)

        # Pop the hierarchy-stack and return it
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

    def elaborate_instance_base(self, inst: _Instance) -> Instantiable:
        """Elaborate a Module Instance, Array or Bundle thereof."""

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
        lines = self.format_hier_path()
        msg = "Elaboration Error at hierarchical path: \n" + "".join(lines) + msg
        # This also serves as a very helpful place for a debugger breakpoint.
        raise RuntimeError(msg)

    def format_hier_path(self) -> List[str]:
        """Create a list of lines describing the current hierarchy path
        Generally intended for debug use, especially in error messages."""

        lines = []
        for s in self.stack:
            # Format: `  Module          MyModule      `
            s_name = s.name or ""
            # Filter out None-valued names, common during elaboration errors.
            line = "  " + type(s).__name__.ljust(14) + s_name.ljust(28)

            source_info = getattr(s, "_source_info", None)
            if source_info is not None:
                # The entry has source/line info. Add it to the error line.

                # For source-paths in the run-directory, print the (presumably shorter) relative-path only
                filepath = source_info.filepath

                # Path.is_relative_to() was added in Python 3.9. And writing a replacement seems harder than you'd think.
                # Use it for Python versions where it works, and skip it for 3.8.
                if (
                    sys.version_info.major > 3 or sys.version_info.minor > 8
                ) and filepath.is_relative_to(Path.cwd()):
                    filepath = filepath.relative_to(Path.cwd())
                else:  # Otherwise print the full absolute path
                    filepath = filepath.resolve()

                # Format: /path/to/file.py:123
                # Serves as a clickable link in popular IDEs.
                line += f"{str(filepath)}:{source_info.linenum}"

            line += "\n"
            lines.append(line)
        return lines
