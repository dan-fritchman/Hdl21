"""
# Array Flattening 
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


class ArrayFlattener(_Elaborator):
    """ 
    Elaboration Pass to Flatten `InstArray`s into `Instance`s, broadcast and remake their connections. 
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modules = dict()  # Module ids to references

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. 
        Primarily performs flattening of Instance Arrays, 
        and re-connecting to the resultant flattened instances  """
        if id(module) in self.modules:  # Already done!
            return module

        if not module.name:
            msg = f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            raise RuntimeError(msg)

        # Flatten Instance arrays
        while module.instarrays:
            name, array = module.instarrays.popitem()
            module.namespace.pop(name)
            # Visit the array's target
            target = self.elaborate_instance_array(array)

            # And do the real work: flattening it.
            if array.n < 1:
                raise RuntimeError(f"Invalid InstArray {array} with size {array.n}")
            # Create the new, flat Instances
            new_insts = []
            for k in range(array.n):
                name = self.flatname(
                    segments=[array.name, str(k)], avoid=module.namespace
                )
                inst = module.add(Instance(of=target, name=name))
                new_insts.append(inst)
            # And connect them
            for portname, conn in array.conns.items():
                if isinstance(conn, BundleInstance):
                    # All new instances get the same BundleInstance
                    for inst in new_insts:
                        inst.connect(portname, conn)
                elif isinstance(conn, (Signal, Slice, Concat)):
                    # Get the target-module port, particularly for its width
                    port = target.ports.get(portname, None)
                    if not isinstance(port, Signal):
                        msg = f"Invalid port connection of `{portname}` {port} to {conn} in InstArray {array}"
                        raise RuntimeError(msg)

                    if port.width == conn.width:
                        # All new instances get the same signal
                        for inst in new_insts:
                            inst.connect(portname, conn)
                    elif port.width * array.n == conn.width:
                        # Each new instance gets a slice, equal to its own width
                        for k, inst in enumerate(new_insts):
                            slize = conn[k * port.width : (k + 1) * port.width]
                            if slize.width != port.width:
                                msg = f"Width mismatch connecting {slize} to {port}"
                                raise RuntimeError(msg)
                            inst.connect(portname, slize)
                    else:  # All other width-values are invalid
                        msg = f"Invalid connection of {conn} of width {conn.width} to port {portname} on Array {array.name} of width {port.width}. "
                        msg += f"Valid widths are either {port.width} (broadcasting across instances) and {port.width * array.n} (individually wiring to each)."
                        raise RuntimeError(msg)
                elif isinstance(conn, PortRef):
                    msg = f"Error elaborating {array} in {module}. "
                    msg += f"Connection {conn} has not been resolved to a `Signal`. "
                    raise RuntimeError
                else:
                    msg = f"Invalid connection to {conn} in InstArray {array}"
                    raise TypeError(msg)

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        # Also visit bundle instances, turning off their pre-elab magic
        for bundle in module.bundles.values():
            self.elaborate_bundle_instance(bundle)

        # Store a reference to the now-expanded Module in our cache, and return it
        self.modules[id(module)] = module
        return module
