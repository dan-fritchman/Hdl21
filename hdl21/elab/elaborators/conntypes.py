"""
# Connection Type Checking 
"""

# Std-Lib Imports
import copy
from typing import Any, Union, get_args

# Local imports
from ...connect import connectable, Connectable
from ...module import Module
from ...instance import InstArray, Instance
from ...signal import Sliceable
from ...bundle import (
    AnonymousBundle,
    BundleInstance,
    BundleRef,
    Bundle,
    resolve_bundle_ref,
)

# Import the base class
from .base import Elaborator, ElabStackEnum


class ConnTypes(Elaborator):
    """ 
    Check for connection-type-validity on each Instance connection. 
    
    "Connection type validity" includes: 
    * All connections must be Signal-like or Bundle-like
    * Signal-valued ports must be connected to Signals of the same width
    * Bundle-valued ports must be connected to Bundles of compatible type 

    Note this stage *does not* perform port-direction checking or modification. 
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Check each Instance's connections in `module` """

        # Check each Instance
        for inst in module.instances.values():
            self.check_instance(module, inst)

        # FIXME: whether to also check arrays.
        # This would require some more smarts about valid broadcast widths.
        # Currently they are checked by a late-stage pass after flattening.
        # for inst in module.instarrays.values():
        #     self.check_instance(module, inst)

        # No errors means it checked out, return the Module unchanged
        return module

    def check_instance(self, module: Module, inst: Union[Instance, InstArray]) -> None:
        """ Check the connections of `inst` in parent `module` """
        self.stack_push(ElabStackEnum.INSTANCE, inst.name)

        # Get the Instance's resolve target, and its bundle-valued IO
        targ = inst._resolved
        io = copy.copy(targ.ports)
        if hasattr(targ, "bundle_ports"):
            io.update(copy.copy(targ.bundle_ports))

        for portname, conn in inst.conns.items():
            # Pop the port from our list
            port = io.pop(portname, None)
            if port is None:
                msg = f"Connection to invalid bundle port {portname} on {inst.name} in {module.name}"
                self.fail(msg)

            # Check its connection-compatibility
            self.assert_compatible(port, conn)

        self.stack_pop()

    def assert_bundles_compatible(
        self, bundle: Bundle, other: Union[BundleInstance, AnonymousBundle]
    ):
        """ Assert that `bundle` is compatible for connection with `other`. 
        Raises a `RuntimeError` if not compatible. 
        This includes key-matching and Signal-width matching, but *does not* examine Signal directions. 
        """

        if isinstance(other, BundleInstance):
            other = other.of
            if other is bundle:
                return None  # Same types, we good

            # Different types. Check each field in `signals` and `bundles` match.
            if sorted(bundle.signals.keys()) != sorted(other.signals.keys()):
                msg = f"Signal names do not match: {bundle.signals.keys()} != {other.signals.keys()}"
                self.fail(msg)

            if sorted(bundle.bundles.keys()) != sorted(other.bundles.keys()):
                msg = f"Bundle names do not match: {bundle.signals.keys()} != {other.signals.keys()}"
                self.fail(msg)

            # Check that each Signal is compatible
            for key, val in bundle.signals.items():
                self.assert_signals_compatible(val, other.signals[key])

            # Recursively check that each Bundle is compatible
            for key, val in bundle.bundles.items():
                self.assert_bundles_compatible(val.of, other.bundles[key].of)

            return None  # Checks out, we good

        if isinstance(other, AnonymousBundle):
            # FIXME: checks on port-refs, signal-widths, etc.
            # For now this just returns success; later checks may often fail where this (eventually) should.
            return None

        msg = f"Invalid connection-compatibility check between {bundle} and {other}"
        raise TypeError(msg)

    def assert_signals_compatible(self, sig: Sliceable, other: Any) -> None:
        """ Assert that `Sliceable`s (generally `Signal`s) a and b are compatible for connection. """

        if not isinstance(other, get_args(Sliceable)):
            self.fail(f"Invalid connection to non-Signal {other}")

        if sig.width != other.width:
            signame = getattr(sig, "name", f"Anonymous(width={sig.width})")
            othername = getattr(other, "name", f"Anonymous(width={other.width})")
            msg = f"Signals `{signame}` and `{othername}` width mismatch: {sig.width} != {other.width}"
            self.fail(msg)

        return None  # Checks out.

    def assert_compatible(self, port: Connectable, conn: Connectable) -> None:
        """ Assert that `port` and `conn` are compatible for connection. """

        if not connectable(conn):
            self.fail(f"Invalid Connection {conn}")

        if isinstance(conn, BundleRef):
            # Recursively call this function on the ref's resolved value
            return self.assert_compatible(port, resolve_bundle_ref(conn))

        if isinstance(port, get_args(Sliceable)):
            return self.assert_signals_compatible(port, conn)

        if isinstance(port, BundleInstance):
            return self.assert_bundles_compatible(port.of, conn)

        raise TypeError(f"Invalid Port {port}")

