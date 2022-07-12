""" 
# `InstanceBundle`s Elaborator Pass

Transform each `InstanceBundle` into a set of "scalar" `Instance`s, 
and reconnect them to the signals of the original `Bundle`. 

This pass is designed to execute relatively early, and relies on `BundleRef`s in particular to 
be resolved *after* it completes. 

FIXME: sort out the relationship between this pass and `ConnTypes`. 
       Currently this pass checks for "bundle type identity" (i.e. `conn.bundle IS inst.bundle`), 
       and `ConnTypes` checks for "structural equivalence". 
FIXME: this is amid `Diff`/`Pair` specific code and more general `InstanceBundle`s
"""

from typing import get_args

# Local imports
from ...module import Module
from ...instance import Instance, InstanceBundle

# Import the base class
from .base import Elaborator


class InstBundleElaborator(Elaborator):
    """ 
    # Instance Bundle Elaborator Pass
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate a Module 
        Remove each Instance Bundle, and replace it with "scalar" Instances. """

        while module.instbundles:
            name, inst = module.instbundles.popitem()
            module.namespace.pop(name)
            self.elaborate_instance_bundle(module, inst)

        return module

    def elaborate_instance_bundle(
        self, module: Module, instbundle: InstanceBundle
    ) -> InstanceBundle:
        """ # Elaborate an Instance Bundle 
        Replace it with "scalar" Instances and reconnect them. """

        from ...bundle import AnonymousBundle, BundleInstance
        from ...signal import Sliceable

        if len(instbundle.bundle.bundles):
            msg = f"Invalid Instance Bundle {instbundle} with nested Bundles"
            self.fail(msg)

        # Create a replacement instance for each Signal in the Bundle
        # Keep a mapping from signal-names to those instances for forthcoming connections
        signal_names_to_instances = {
            signame: module.add(
                name=self.flatname(
                    segments=[instbundle.name, signame], avoid=module.namespace
                ),
                val=Instance(of=instbundle.of),
            )
            for signame in instbundle.bundle.signals
        }

        # Disconnect each port from the `InstanceBundle`, and map it into the new scalar `Instance`s
        for portname in list(instbundle.conns.keys()):
            conn = instbundle.disconnect(portname)

            if isinstance(conn, BundleInstance):
                # If the connection is a Bundle instance, connect each new instance to the paired-named Signals

                if conn.of is not instbundle.bundle:
                    msg = f"Invalid Instance Bundle connection between {conn.of} and {instbundle.bundle}"
                    self.fail(msg)

                for signame, new_inst in signal_names_to_instances.items():
                    new_inst.connect(portname, conn._bundle_ref(signame))

            elif isinstance(conn, AnonymousBundle):
                for signame, new_inst in signal_names_to_instances.items():
                    new_inst.connect(portname, conn.get(signame))

            elif isinstance(conn, get_args(Sliceable)):
                # If the connection is a scalar, connect it to each new instance
                if conn.width != 1:
                    msg = f"InstanceBundle {instbundle.name} connection {conn} is not a scalar, but has width {conn.width}"
                    self.fail(msg)

                for new_inst in signal_names_to_instances.values():
                    new_inst.connect(portname, conn)

            else:
                self.fail(
                    f"Invalid connection {conn} for `InstanceBundle` {instbundle.name}"
                )

        return instbundle
