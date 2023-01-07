"""
# PortRef Resolution 

Creates concrete `Signal`s and `BundleInstance`s to replace `PortRef`s.
"""

# Std-Lib Imports
import copy
from typing import Union, List, Optional, Dict

# Local imports
from ...connect import Connectable
from ...instance import _get_connref
from ...instantiable import io
from ...module import Module
from ...portref import PortRef
from ...bundle import BundleInstance, BundleRef, AnonymousBundle
from ...signal import PortDir, Signal, Visibility
from ...noconn import NoConn
from .resolve_ref_types import update_ref_deps

# Import the base class
from .base import Elaborator

# Union of the types which serve as "source signals",
# i.e. the things which we are resolve `PortRef`s *to*.
# If we find one of these connected to a group of connected ports,
# it becomes the replacement connection for all of them.
Source = Union[Signal, BundleInstance, BundleRef, AnonymousBundle]

# Union of the types which can serve as (generalized) Ports:
# either Signals or Bundle Instances
PortType = Union[Signal, BundleInstance]


class ResolvePortRefs(Elaborator):
    """Resolve all `PortRef`s on all `Instance`s.

    This pass resolves "Instance to Instance" connections such as:
    ```
    inst1 = Module1()
    inst2 = Module2(port2=inst1.port1)
    ```

    After this pass, all such connections resolve to concrete
    connectable objects, all of which are members of the `Source` type-union
    defined above.

    While not terribly consistent with its name, this pass also resolves
    all `NoConn` connections into concrete `Signal`s, or fails if any `NoConn`s
    are invalidly connected between one another.
    """

    def elaborate_module(self, module: Module) -> Module:
        """
        Resolve and replace all Instance `PortRef`s in `module`.

        In the process, all `Connectable`s are annotated with a set of `_connected_ports`.
        These `_connected_ports` are relied upon by later elaboration stages,
        and must be maintained hereafter, e.g. when making connection updates.
        """

        instancelike = (
            list(module.instances.values())
            + list(module.instarrays.values())
            + list(module.instbundles.values())
        )

        # Collect up all `PortRef`s for all instances in the module
        # FIXME: move from SetList to a regular Set. Thus far breaks one test, somehow.
        module_portrefs = SetList()
        for inst in instancelike:

            # Populate the module-level set of PortRefs
            for portref in inst._refs.portrefs.values():
                module_portrefs.add(portref)

            # FIXME: add the `NoConn`s here, although it's not clear we *really* need these checks on them
            for portname, conn in inst.conns.items():
                if isinstance(conn, NoConn):
                    module_portrefs.add(_get_connref(inst, portname))

        def follow(pref: PortRef, group: SetList) -> None:
            """Closure to recursively follow `pref`, adding its outward and inward connections to `group`.
            Removes encountered entries from `module_portrefs` along the way."""

            if pref in group:
                return  # Already done
            if pref in module_portrefs:
                module_portrefs.remove(pref)

            # Add the portref to the group
            group.add(pref)

            # Add, and if necessary recursively follow, its instance connection
            conn = pref.inst.conns.get(pref.portname, None)
            if isinstance(conn, PortRef):
                follow(conn, group)
            else:  # Add ultimate signal `Source`s to the group
                group.add(conn)

            # And recursively follow its connected ports
            for connected_port in pref._connected_ports:
                follow(connected_port, group)

        # Collect groups of connected `PortRef`s
        groups: List[List[Optional[Connectable]]] = list()

        while module_portrefs:
            # Create a new group, and recursively follow port refs to populate it
            group = SetList()
            follow(module_portrefs.pop(), group)

            # Filter out the `None` entries before sticking in the `groups` list-of-lists.
            group: List[Connectable] = [x for x in group.order if x is not None]
            groups.append(group)

        # For each group, find and/or create a Signal to replace all the PortRefs with.
        for group in groups:
            self.handle_group(module, group)

        return module

    def handle_group(self, module: Module, group: List[Connectable]) -> None:
        """Handle a `group` worth of connected Ports and NoConns"""

        # First cover `NoConn` connections, checking for any invalid multiple-conns to them.
        if any([isinstance(n, NoConn) for n in group]):
            return self.handle_noconn(module, group)
        return self.handle_portconn(module, group)

    def handle_portconn(self, module: Module, group: List[Connectable]):
        """Handle re-connecting a list of connected `PortRef`s.
        Creates and adds a fresh new `Signal` if one does not already exist."""

        group_port_refs = [x for x in group if isinstance(x, PortRef)]

        # Find any existing, declared `Source` connected to `group`.
        # And if we don't find any, go about naming and creating one.
        source: Optional[Source] = self.find_source(group)
        if source is None:
            source = self.create_source(module, group_port_refs)

        # Resolve each PortRef with `source` as its referent,
        # and reconnect it everywhere it's connected.
        for portref in group_port_refs:
            resolve_portref(portref, source)

    def find_source(self, group: List[Connectable]) -> Optional[Source]:
        """Find any existing, declared `Source` connected to `group`.
        Returns None is no `Source`s are connected to any element in the group."""

        # Extract which of the `group` are connected to `Source`s
        sources: List[Source] = [s for s in group if isinstance(s, Source.__args__)]

        # Three relevant cases then emerge:
        # * (a) Zero sources. No problem, create one.
        # * (b) A single source. Also good; this will be connected to all other ports in the group.
        # * (c) More than one source.
        #   * This *shouldn't* be possible. If it is possible, we haven't figured out how.
        #   * This method raises a `RuntimeError` if this somehow happens.

        if len(sources) == 0:
            return None
        if len(sources) == 1:
            return sources[0]

        # More than one source, somehow. Error time.
        msg = f"Internal error: invalid connection, with multiple Source-Signals {sources}, "
        msg += f"shorting Ports {[(p.inst.name, p.portname) for p in group]}"
        self.fail(msg)

    def which_portref_to_name(self, group: List[PortRef]) -> PortRef:
        """Figure out which PortRef in `group` to use for its new signal name.
        This generally follows "the port the other ones refer to", i.e. for:
        ```
        i1.p = i0.p
        i2.p = i0.p
        i3.p = i1.p
        i4.p = i3.p
        ```
        The Instance `i0` has the sole None-connected Port `p`, and gets "naming rights".

        In other cases there is no such instance, such as:
        ```
        i0.p = i1.p
        i1.p = i0.p # Connected back!
        ```
        In these cases, the first Instance name in alphabetical order is used.
        """

        # Sort out which PortRefs have no connection
        conn = lambda p: p.inst.conns.get(p.portname, None)
        connected_to_none = [p for p in group if conn(p) is None]

        if len(connected_to_none) == 1:
            return connected_to_none[0]

        if len(connected_to_none) > 1:
            self.fail(f"Invalid PortRef group: {group}")

        # Nothing "unconnected". Find the instance one with the lowest (alphabetical) name.
        ordered = sorted(group, key=lambda p: p.inst.name)
        return ordered[0]

    def create_source(self, module: Module, group: List[PortRef]) -> PortType:
        """Create a new `Signal`, parametrized and named to connect to the `PortRef`s in `group`."""
        from ...instantiable import io

        # Sort out which PortRef to use for the new signal name.
        portref = self.which_portref_to_name(group)

        # Get its Module for its IO
        # Note if the other entries in `group` have incompatible IO, this will be flagged by a later pass.
        ios = io(portref.inst._resolved)

        port = ios.get(portref.portname, None)
        if port is None:  # Clone it, and remove any Port-attributes
            msg = f"Invalid port `{portref.portname}` on Instance `{portref.inst.name}` in Module `{module.name}`"
            self.fail(msg)

        # Copy that port into an internal Signal / Bundle
        sig = self.copy_port(port)

        # Rename it and add it to the Module namespace
        signame = self.flatname(
            segments=[f"{portref.inst.name}_{portref.portname}"],
            avoid=module.namespace,
        )
        sig.name = signame
        module.add(sig)
        return sig

    def copy_port(self, port: PortType) -> PortType:
        """Copy a port into an internal Signal or BundleInstance"""

        if isinstance(port, Signal):
            # Make a copy, and update its port-level visibility to internal
            sig = copy.copy(port)
            sig.vis = Visibility.INTERNAL
            sig.direction = PortDir.NONE
            return sig

        if isinstance(port, BundleInstance):
            # Copy the bundle, removing port and role fields.
            return BundleInstance(of=port.of, port=False, role=None)

        self.fail(f"Invalid Port Type `{port}`")

    def handle_noconn(self, module: Module, group: List[Connectable]):
        """Handle a group with a `NoConn`."""
        # First check for validity of the group, i.e. that the `NoConn` only connects to *one* port.
        if len(group) > 2:
            msg = f"Invalid multiply-connected `NoConn`, including {group} in {module}"
            self.fail(msg)
        # So `group` has two entries: a `NoConn` and a `PortRef`
        if isinstance(group[0], NoConn):
            return self.replace_noconn(module, portref=group[1], noconn=group[0])
        return self.replace_noconn(module, portref=group[0], noconn=group[1])

    def replace_noconn(self, module: Module, portref: PortRef, noconn: NoConn):
        """Replace `noconn` with a newly minted `Signal` or `BundleInstance`."""

        # Get the target Module's port-object corresponding to `portref`
        io_dict: Dict[str, Connectable] = io(portref.inst._resolved)
        port = io_dict.get(portref.portname, None)
        if port is None:
            msg = f"Invalid port connection to `{portref}` in Module `{module}`"
            self.fail(msg)

        # Copy any relevant attributes of the Port
        sig = self.copy_port(port)

        # Set the signal name, either from the NoConn or the instance/port names
        if noconn.name is not None:
            sig.name = noconn.name
        else:
            sig.name = self.flatname(
                segments=[f"{portref.inst.name}_{portref.portname}"],
                avoid=module.namespace,
            )

        # Add the new signal, and connect it to `inst`
        module.add(sig)
        portref.inst.connect(portref.portname, sig)


class SetList:
    """A common combination of a hash-set and ordered list of the same items.
    Used for keeping ordered items while maintaining quick membership testing.

    FIXME: this is really using a LIST for now, slowing down membership tests,
    but should be set-based when some connectable types, particularly `Signal`, are ready for it.
    """

    def __init__(self):
        # self.set = set()
        self.list = list()

    def __bool__(self):
        return bool(self.list)

    def __contains__(self, item):
        # return item in self.set
        return item in self.list

    def add(self, item):
        # if item not in self.set:
        if item not in self.list:
            # self.set.add(item)
            self.list.append(item)

    def remove(self, item):
        # if item not in self.set:
        if item not in self.list:
            raise RuntimeError
            # self.set.add(item)
        self.list.remove(item)

    def pop(self):
        # if item not in self.set:
        if not self.list:
            raise RuntimeError
            # self.set.add(item)
        return self.list.pop(0)

    @property
    def order(self):
        return self.list


def resolve_portref(pref: PortRef, to: Connectable) -> None:
    """# Resolve a `PortRef` to its referent `Connectable`."""

    if pref.resolved is to:
        return  # Already resolved
    if pref.resolved is not None:
        raise ValueError(f"PortRef {pref} already resolved")

    # Give the `PortRef` a reference to its referent
    pref.resolved = to

    # Connect the "primary" instance to the referent
    # Note this differs between `PortRef` and `BundleRef`;
    # the latter has no "primary instance" to connect to.
    pref.inst.connect(pref.portname, to)

    # Update all downstream dependencies, e.g. connected ports, slices
    update_ref_deps(pref, to)
