"""
# Connection Type Checking 
"""

# Std-Lib Imports
import copy
from typing import Union

# Local imports
from ...connect import connectable
from ...module import Module
from ...instance import InstArray, Instance
from ...bundle import AnonymousBundle, BundleInstance, _check_compatible

# Import the base class
from .base import Elaborator


class BundleConnTypes(Elaborator):
    """ Check for connection-type-validity on each Bundle-valued connection. 
    Note this stage *does not* perform port-direction checking or modification. 
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Check each Instance's connections in `module` """

        # Check each Instance
        for inst in module.instances.values():
            self.check_instance(module, inst)
        for inst in module.instarrays.values():
            self.check_instance(module, inst)

        # No errors means it checked out, return the Module unchanged
        return module

    def check_instance(self, module: Module, inst: Union[Instance, InstArray]) -> None:
        """ Check the connections of `inst` in parent `module` """

        # Get the Instance's resolve target, and its bundle-valued IO
        targ = inst._resolved
        if hasattr(targ, "bundle_ports"):
            io = copy.copy(targ.bundle_ports)
        else:
            # Still check on no-bundle Instances (e.g. Primitives),
            # Mostly to ensure no *connections* are errantly Bundle-valued.
            io = dict()
        # And filter out the bundle-valued connections
        conns = {
            k: v
            for k, v in inst.conns.items()
            if isinstance(v, (BundleInstance, AnonymousBundle))
        }

        for portname, conn in conns.items():
            # Pop the port from our list
            port = io.pop(portname, None)
            if port is None:
                msg = f"Connection to invalid bundle port {portname} on {inst.name} in {module.name}"
                raise RuntimeError(msg)

            if (  # Check its Bundle type.
                not isinstance(conn, (BundleInstance, AnonymousBundle))
                or not isinstance(port, BundleInstance)
                ## FIXME: this is the "exact type equivalence" so heavily debated. Disabled.
                # or conn.of is not port.of ## <= there
            ):
                msg = f"Invalid Bundle Connection between {conn} and {port} on {inst.name} in {module.name}"
                raise RuntimeError(msg)
            # Check its connection-compatibility
            _check_compatible(port.of, conn)

        # Check for anything left over.
        bad = dict()
        while io:
            # Unconnected bundle-ports are not *necessarily* an error, since they can be connected signal-by-signal.
            # Check whether each remaining `io` has a corresponding `PortRef`, an indication of a connection.
            # More-specific checking of their validity will come later, with other Signals.
            name, conn = io.popitem()
            if name not in inst.portrefs:
                bad[name] = conn

        if len(bad):  # Now, anything left over is an error.
            msg = f"Unconnected Bundle Port(s) {list(bad.keys())} on Instance {inst.name} in Module {module.name}"
            raise RuntimeError(msg)

        return module


class SignalConnTypes(Elaborator):
    """ Check for connection-type-validity between each Instance and its connections. 
    "Connection type validity" includes: 
    * All connections must be Signal-like or Bundle-like
    * Signal-valued ports must be connected to Signals of the same width
    * Bundle-valued ports must be connected to Bundles of the same type 
    Note this stage may be run after Bundles have been flattened, in which case the Bundle-checks perform no-ops. 
    They are left in place nonetheless. 
    Note this stage *does not* perform port-direction checking or modification. 
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Check each Instance's connections in `module` """

        # Check each Instance
        for inst in module.instances.values():
            self.check_instance(module, inst)
        for inst in module.instarrays.values():
            self.check_instance(module, inst)

        # No errors means it checked out, return the Module unchanged
        return module

    def check_instance(self, module: Module, inst: Instance) -> None:
        """ Check the connections of `inst` in parent `module` """

        # Get the Instance's resolve target, and its IO
        targ = inst._resolved
        # FIXME: make this `io` method Module-like-wide
        io = copy.copy(targ.ports)
        if hasattr(targ, "bundle_ports"):
            io.update(copy.copy(targ.bundle_ports))

        for portname, conn in inst.conns.items():
            # Pop the port from our list
            port = io.pop(portname, None)
            if port is None:
                msg = f"Connection to invalid port {portname} on {inst.name} in {module.name}"
                raise RuntimeError(msg)
            # Checks
            if isinstance(conn, BundleInstance):
                # Identity-check the target Bundle
                if conn.of is not port.of:
                    msg = f"Invalid Bundle Connection between {conn} and {port} on {inst.name} in {module.name}"
                    raise RuntimeError(msg)
            elif connectable(conn):
                # For scalar Signals, check that widths match up
                if conn.width != port.width:
                    msg = f"Invalid Connection between {conn} of width {conn.width} and {port} of width {port.width} on {inst.name} in {module.name}"
                    raise RuntimeError(msg)
            else:
                msg = f"Invalid connection {conn} on {inst.name} in {module.name}"
                raise TypeError(msg)

        if len(io):  # Check for anything left over
            raise RuntimeError(f"Unconnected IO {io} on {inst.name} in {module.name}")
