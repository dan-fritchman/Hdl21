""" 
# Differential Pair Elaborator Pass
"""

from typing import get_args

# Local imports
from ...module import Module
from ...diff_pair import Diff, Pair

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

    def elaborate_instance_bundle(self, module: Module, inst: Pair) -> Pair:
        """ # Elaborate an Instance Bundle 
        Replace it with "scalar" Instances and reconnect them. """

        from ...bundle import AnonymousBundle, BundleInstance
        from ...instance import Instance
        from ...signal import Sliceable

        # Create the two replacement instances
        inst_p, inst_n = Instance(of=inst.of), Instance(of=inst.of)
        
        for portname, conn in inst.conns.items(): 
            if isinstance(conn, BundleInstance):
                if conn.of is not inst.bundle:
                    raise ValueError
                # If the connection is a `Diff` instance, connect each leg to a new instance
                inst_p.connect(portname, conn.signals["p"])
                inst_n.connect(portname, conn.signals["n"])
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
