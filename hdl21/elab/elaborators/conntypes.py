"""
# Connection Type Checking 
"""

# Std-Lib Imports
import copy
from typing import Any, Union, Dict

# PyPi Imports
from pydantic.dataclasses import dataclass

# Local imports
from ...connect import is_connectable, Connectable
from ...portref import PortRef
from ...module import Module
from ...instance import Instance
from ...noconn import NoConn
from ...bundle import (
    AnonymousBundle,
    BundleInstance,
    BundleRef,
    Bundle,
)
from .width import width, HasWidth
from ...instantiable import (
    io,
    Instantiable,
    GeneratorCall,
    ExternalModuleCall,
    PrimitiveCall,
)

# Import the base class
from .base import Elaborator


"""
Connection Statuses
"""


class Valid:
    # Valid connection
    ...  # empty


@dataclass
class NoPort:
    name: str

    def __repr__(self) -> str:
        return f"Connection to non-existent Port `{self.name}`"


@dataclass
class Unconnected:
    name: str

    def __repr__(self) -> str:
        return f"Missing connection to Port `{self.name}`"


@dataclass
class InvalidType:
    msg: str  # Free-form error message

    def __repr__(self) -> str:
        return self.msg


# The union of these things is a `ConnStatus`
ConnStatus = Union[Valid, NoPort, Unconnected, InvalidType]


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
        """Check each Instance's connections in `module`"""

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

    def check_instance(self, module: Module, inst: Instance) -> None:
        """Check the connections of `inst` in parent `module`"""
        self.stack.append(inst)

        # Get copies of both the instance's ports and connections.
        # These will be two {str: Connectable} dictionaries, who should have the same keys,
        # and each paired value should be connection-compatible.
        conns = copy.copy(inst.conns)
        io = io_for_checking(parent=module, i=inst._resolved)

        # Track the status of each connection, so we can report the Instance-wide state if there are errors.
        statuses: Dict[str, ConnStatus] = dict()

        for portname, port in io.items():
            # Get the corresponding connection
            conn = conns.pop(portname, None)
            if conn is None:
                statuses[portname] = Unconnected(portname)
            else:  # Check its connection-compatibility
                statuses[portname] = self.check_compatible(port, conn)

        # Now check if anything remains in `conns`, i.e. that there are invalid connections to nonexistent ports.
        for conn_name in conns.keys():
            statuses[conn_name] = NoPort(conn_name)

        # Look for any non-`Valid` connections. And if we have any, fail.
        bad_conns = {
            name: s for name, s in statuses.items() if not isinstance(s, Valid)
        }
        if bad_conns:
            msg = f"Invalid connections `{bad_conns}` on Instance `{inst.name}` in Module `{module.name}`"
            self.fail(msg)

        self.stack.pop()  # Checks out, we good, pop this Instance from our elab-stack.

    def check_bundles_compatible(
        self, bundle: Bundle, other: Union[BundleInstance, AnonymousBundle]
    ) -> ConnStatus:
        """Assert that `bundle` is compatible for connection with `other`.
        Raises a `RuntimeError` if not compatible.
        This includes key-matching and Signal-width matching, but *does not* examine Signal directions.
        """

        if isinstance(other, BundleInstance):
            other = other.of
            if other is bundle:
                return Valid()  # Same types, we good

            # Different types. Check each field in `signals` and `bundles` match.
            if sorted(bundle.signals.keys()) != sorted(other.signals.keys()):
                msg = f"Signal names do not match: {bundle.signals.keys()} != {other.signals.keys()}"
                return InvalidType(msg)

            if sorted(bundle.bundles.keys()) != sorted(other.bundles.keys()):
                msg = f"Bundle names do not match: {bundle.signals.keys()} != {other.signals.keys()}"
                return InvalidType(msg)

            # Check that each Signal is compatible
            for key, val in bundle.signals.items():
                sts = self.check_signals_compatible(val, other.signals[key])
                if not isinstance(sts, Valid):
                    return sts

            # Recursively check that each Bundle is compatible
            for key, val in bundle.bundles.items():
                sts = self.check_bundles_compatible(val.of, other.bundles[key].of)
                if not isinstance(sts, Valid):
                    return sts

            return Valid()  # Checks out, we good

        if isinstance(other, AnonymousBundle):
            # FIXME: checks on port-refs, signal-widths, etc.
            # For now this just returns success; later checks may often fail where this (eventually) should.
            return Valid()

        msg = f"Invalid connection-compatibility check between {bundle} and {other}"
        self.fail(msg)

    def check_signals_compatible(self, sig: HasWidth, other: Any) -> ConnStatus:
        """Assert that `HasWidth`s (generally `Signal`s) a and b are compatible for connection."""

        if not isinstance(other, HasWidth.__args__):
            msg = f"Invalid connection to non-Signal {other}"
            return InvalidType(msg)

        if self.get_width(sig) != self.get_width(other):
            signame = getattr(sig, "name", f"Anonymous(width={sig.width})")
            othername = getattr(other, "name", f"Anonymous(width={other.width})")
            msg = f"Signals `{signame}` and `{othername}` width mismatch: {sig.width} != {other.width}"
            return InvalidType(msg)

        return Valid()  # Checks out.

    def check_compatible(self, port: Connectable, conn: Connectable) -> ConnStatus:
        """Assert that `port` and `conn` are compatible for connection."""

        if not is_connectable(conn):
            return InvalidType(f"Invalid Connection {conn}")

        if isinstance(conn, BundleRef):
            # Recursively call this function on the ref's resolved value
            from .resolve_ref_types import resolve_bundleref_type

            referent = resolve_bundleref_type(conn, self.fail)
            return self.check_compatible(port, referent)

        if isinstance(port, HasWidth.__args__):
            return self.check_signals_compatible(port, conn)

        if isinstance(port, BundleInstance):
            return self.check_bundles_compatible(port.of, conn)

        self.fail(f"Invalid Port {port}")

    def get_width(self, conn: Connectable) -> int:
        """Get the `width` of a conn. Fails for types which this pass is not designed to handle."""

        if isinstance(conn, (NoConn, PortRef)):
            msg = f"Internal error: {type(conn).__name__} remaining in connection-types check"
            return self.fail(msg)

        return width(conn, failer=self.fail)


def io_for_checking(parent: Module, i: Instantiable) -> Dict[str, "Connectable"]:
    """Get the relevant IOs of Instantiable `i` for checking.
    Depending on the elaboration state of `parent` and `i`, this may include the "bundled" or "flattened" IOs."""

    if isinstance(i, GeneratorCall):
        # Take the result of the generator call
        i = i.result

    if isinstance(i, (ExternalModuleCall, PrimitiveCall)):
        # These do not have Bundle-valued ports
        return copy.copy(i.ports)

    if not isinstance(i, Module):
        raise TypeError(f"Invalid Instantiable: {i}")

    # OK we've got a Module.
    # Whether to check the "bundled" or "flattened" IO is dependent on
    # whether the *parent* and `i` have or haven't been flattened.
    parent_flattened = parent._pre_flattening_io is not None
    child_flattened = i._pre_flattening_io is not None

    if parent_flattened and not child_flattened:
        msg = f"Error child {i} has not been elaborated before parent {parent}"
        raise RuntimeError(msg)

    if parent_flattened != child_flattened:
        # Mismatch between parent and child status.
        # Return the child IOs from just *before* the flattening pass.
        return copy.copy(i._pre_flattening_io)

    # Parent and child statuses match, whether flattened or not.
    # Return the child IOs as they are now.
    return io(i)
