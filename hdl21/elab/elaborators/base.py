"""
# Base Elaborator
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

from ..elaboratable import Elabable
from ..context import Context


class _Elaborator:
    """ Base Elaborator Class """

    @classmethod
    def elaborate(cls, top, ctx):
        """ Elaboration entry-point. Elaborate the top-level object. """
        return cls(top, ctx).elaborate_top()

    def __init__(self, top: Elabable, ctx: Context):
        self.top = top
        self.ctx = ctx

    def elaborate_top(self):
        """ Elaborate our top node """
        if not isinstance(self.top, Module):
            raise TypeError
        return self.elaborate_module(self.top)

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """ Elaborate a GeneratorCall """
        # Only the generator-elaborator can handle generator calls; default it to error on others.
        raise RuntimeError(f"Invalid call to elaborate GeneratorCall by {self}")

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate a Module """
        # Required for all passes. Defaults to `NotImplementedError`.
        raise NotImplementedError

    def elaborate_external_module(self, call: ExternalModuleCall) -> ExternalModuleCall:
        """ Elaborate an ExternalModuleCall """
        # Default: nothing to see here, carry on
        return call

    def elaborate_primitive_call(self, call: PrimitiveCall) -> PrimitiveCall:
        """ Elaborate a PrimitiveCall """
        # Default: nothing to see here, carry on
        return call

    def elaborate_bundle_instance(self, inst: BundleInstance) -> None:
        """ Elaborate an BundleInstance """
        # Annotate each BundleInstance so that its pre-elaboration `PortRef` magic is disabled.
        inst._elaborated = True

    def elaborate_bundle(self, bundle: Bundle) -> Bundle:
        """ Elaborate an Bundle """
        # Default: nothing to see here, carry on
        return bundle

    def elaborate_instance_array(self, array: InstArray) -> Instantiable:
        """ Elaborate an InstArray """
        # Turn off `PortRef` magic
        array._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(array._resolved)

    def elaborate_instance(self, inst: Instance) -> Instantiable:
        """ Elaborate a Module Instance. """
        # This version of `elaborate_instantiable` is the "post-generators" version used by *most* passes.
        # The Generator-elaborator is different, and overrides it.

        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(inst._resolved)

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        # This version of `elaborate_instantiable` is the "post-generators" version used by *most* passes.
        # The Generator-elaborator is different, and overrides it.
        if not of:
            raise RuntimeError(f"Error elaborating undefined Instance-target {of}")
        if isinstance(of, Module):
            return self.elaborate_module(of)
        if isinstance(of, PrimitiveCall):
            return self.elaborate_primitive_call(of)
        if isinstance(of, ExternalModuleCall):
            return self.elaborate_external_module(of)
        raise TypeError

    @staticmethod
    def flatname(
        segments: List[str], *, avoid: Optional[Dict] = None, maxlen: int = 511
    ) -> str:
        """ Create a attribute-name merging string-list `segments`, while avoiding all keys in dictionary `avoid`.
        Commonly re-used while flattening  nested objects and while creating explicit attributes from implicit ones. 
        Raises a `RunTimeError` if no such name can be found of length less than `maxlen`. 
        The default max-length is 511 characters, a value representative of typical limits in target EDA formats. """

        if avoid is None:
            avoid = {}

        # The default format and result is of the form "seg0_seg1".
        # If that is in the avoid-keys, append underscores until it's not, or fails.
        name = "_".join(segments)
        while True:
            if len(name) > maxlen:
                msg = f"Could not generate a flattened name for {segments}: (trying {name})"
                raise RuntimeError(msg)
            if name not in avoid:  # Done!
                break
            name += "_"  # Collision; append underscore
        return name
