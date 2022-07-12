""" 
# Differential Pair Elaborator Pass

# FIXME: this is amid `Diff`/`Pair` specific code and more general `InstanceBundle`s
"""

from typing import get_args

# Local imports
from ...module import Module
from ...instance import Instance, InstanceBundle

# Import the base class
from .base import Elaborator


class DiffPairElaborator(Elaborator):
    """ 
    # Differential Pair Elaborator Pass
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate a Module 
        Remove each Instance Bundle, and replace it with "scalar" Instances. """

        while(module.instbundles):
            name, inst = module.instbundles.popitem()
            module.namespace.pop(name)
            self.elaborate_instance_bundle(module, inst)
        
        return module

    def elaborate_instance_bundle(self, module: Module, inst: InstanceBundle) -> InstanceBundle:
        """ # Elaborate an Instance Bundle 
        Replace it with "scalar" Instances and reconnect them. """

        from ...bundle import AnonymousBundle, BundleInstance
        from ...signal import Sliceable

        # Create a replacement instance for each Signal in the Bundle
        name_p = self.flatname(
            segments=[inst.name, "p"],
            avoid=module.namespace,
        )
        name_n = self.flatname(
            segments=[inst.name, "n"],
            avoid=module.namespace,
        )
        inst_p, inst_n = Instance(name=name_p, of=inst.of), Instance(name=name_n, of=inst.of)
        module.add(inst_p)
        module.add(inst_n)
        
        # Disconnect each port from the `InstanceBundle`, and map it into the new scalar `Instance`s
        for portname in list(inst.conns.keys()): 
            conn = inst.disconnect(portname)

            if isinstance(conn, BundleInstance):
                if conn.of is not inst.bundle:
                    raise ValueError
                # If the connection is a `Diff` instance, connect each leg to a new instance
                inst_p.connect(portname, conn._bundle_ref("p"))
                inst_n.connect(portname, conn._bundle_ref("n"))
            elif isinstance(conn, AnonymousBundle):
                # FIXME: where to stick the checking for "diff compatibility"
                raise NotImplementedError # FIXME!
            elif isinstance(conn, get_args(Sliceable)):
                # If the connection is a scalar, connect it to both new instances
                if conn.width != 1: 
                    msg = f"Pair {inst.name} connection {conn} is not a scalar, but has width {conn.width}"
                    raise ValueError(msg)
                inst_p.connect(portname, conn)
                inst_n.connect(portname, conn)
            else:
                msg = f"Invalid connection {conn} for `Pair` {inst.name}"
                raise TypeError(msg)

        return inst 
