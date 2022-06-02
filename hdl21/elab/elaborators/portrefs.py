"""
# PortRef Resolution 

Creates concrete `Signal`s and `BundleInstance`s to replace `PortRef`s.
"""

# Std-Lib Imports
import copy
from typing import Union, Dict, List, Optional, Sequence, get_args

# Local imports
from ...module import Module
from ...instance import PortRef, Instance, InstArray
from ...bundle import BundleInstance, BundleRef, AnonymousBundle
from ...signal import PortDir, Signal, Visibility, NoConn

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
    """ Resolve all `PortRef`s on all `Instance`s. 
    
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
        """ Resolve and replace all Instance `PortRef`s in `module`. """

        # Collect up every `PortRef` and `NoConn` that's been instantiated
        portconns = self.collect_portconns(module)
        # And replace them with concrete connectable types
        self.replace_portconns(module, portconns)

        return module

    def collect_portconns(
        self, module: Module
    ) -> Dict[PortRef, Union[PortRef, NoConn]]:
        """ Collect a dictionary of all Instance-ports connected to `PortRef`s or `NoConn`s. """

        portconns: Dict[PortRef, Union[PortRef, NoConn]] = dict()

        # FIXME: a better word for "instances or arrays thereof"; we already used "connectable"
        connectables = list(module.instances.values()) + list(
            module.instarrays.values()
        )
        for inst in connectables:
            for port, conn in inst.conns.items():
                if isinstance(conn, (PortRef, NoConn)):
                    internal_ref = PortRef(inst, port)
                    portconns[internal_ref] = conn

        return portconns

    def replace_portconns(
        self, module: Module, portconns: Dict[PortRef, Union[PortRef, NoConn]]
    ) -> Module:
        """ Replace each port-to-port connection in `portconns` with concrete `Signal`s. """

        # Now walk through all port-connections, assigning each set to a net
        groups: List[List[Union[PortRef, NoConn]]] = list()

        while portconns:
            # Keep both a list for consistent ordering, and a set for quick membership tests
            this_group = SetList()
            # Grab a random pair
            inner, outer = portconns.popitem()
            this_group.add(inner)
            this_group.add(outer)
            # If it's connected to others, grab those
            while outer in portconns:
                outer = portconns.pop(outer)
                this_group.add(outer)
            # Once we find an object not in `portconns`, we've covered everything connected to the group.
            groups.append(this_group.order)

        # For each group, find and/or create a Signal to replace all the PortRefs with.
        for group in groups:
            self.handle_group(module, group)

        return module

    def handle_group(self, module: Module, group: List[Union[PortRef, NoConn]]):
        """ Handle a `group` worth of connected Ports and NoConns """

        # First cover `NoConn` connections, checking for any invalid multiple-conns to them.
        if any([isinstance(n, NoConn) for n in group]):
            return self.handle_noconn(module, group)
        return self.handle_portconn(module, group)

    def handle_portconn(self, module: Module, group: List[PortRef]):
        """ Handle re-connecting a list of connected `PortRef`s. 
        Creates and adds a fresh new `Signal` if one does not already exist. """

        # Find any existing, declared `Signal` connected to `group`.
        # And if we don't find any, go about naming and creating one.
        sig: Source = self.find_source(group) or self.create_source(module, group)

        # if sig is None:
        #     sig = self.create_source(module, group)

        # And re-connect it to each Instance
        non_sources = list(filter(lambda p: self.source(p) is None, group))
        for portref in non_sources:
            portref.inst.conns[portref.portname] = sig

    @staticmethod
    def source(portref: PortRef) -> Optional[Source]:
        """ 
        Find the "source signal" for `portref`, if one is connected. 
        If `portref` is not explicitly connected, or is connected to another `PortRef`, returns None. 
        """
        if not isinstance(portref.inst, (Instance, InstArray)):
            raise TypeError(f"PortRef instance {portref}")

        portconn = portref.inst.conns.get(portref.portname, None)
        if portconn is None:
            return None  # Nothing explicitly connected *into* this port
        if isinstance(portconn, PortRef):
            return None  # Connected to another `PortRef`, not a `Source`

        # This check *should* always succeed, but type-check it nonetheless.
        if isinstance(portconn, get_args(Source)):
            return portconn
        raise TypeError(f"Connection {portconn}")

    def find_source(self, group: List[PortRef]) -> Optional[Source]:
        """ Find any existing, declared `Source` connected to `group`. 
        And if there more than one, make sure they all connect to the same object. 
        Returns None is no `Source`s are connected to any element in the group. """

        # Extract which of the `group` are connected to `Source`s
        sources: Sequence[Optional[Source]] = map(self.source, group)
        sources: List[Source] = [s for s in sources if s is not None]

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
        raise RuntimeError(msg)

    def create_source(self, module: Module, group: List[PortRef]) -> PortType:
        """ Create a new `Signal`, parametrized and named to connect to the `PortRef`s in `group`. """

        # Find a unique name for the new Signal.
        # The default name template is "_inst1_port1_inst2_port2_inst3_port3_"
        signame = self.flatname(
            segments=[f"{p.inst.name}_{p.portname}" for p in group],
            avoid=module.namespace,
        )

        # Create the Signal, looking up all its properties from the last Instance's Module
        # (If other instances are inconsistent, later stages will flag them)
        portref = group[-1]
        lastmod = portref.inst._resolved

        # FIXME: make this `io` method Module-like-wide
        io = copy.copy(lastmod.ports)
        if hasattr(lastmod, "bundle_ports"):
            io.update(copy.copy(lastmod.bundle_ports))

        port = io.get(portref.portname, None)
        if port is None:  # Clone it, and remove any Port-attributes
            msg = f"Invalid port {portref.portname} on Instance {portref.inst.name} in Module {module.name}"
            raise RuntimeError(msg)

        # Copy that port into an internal Signal / Bundle
        sig = self.copy_port(port)

        # Rename it and add it to the Module namespace
        sig.name = signame
        module.add(sig)
        return sig

    @staticmethod
    def copy_port(port: PortType) -> PortType:
        """ Copy a port into an internal Signal or BundleInstance """

        if isinstance(port, Signal):
            # Make a copy, and update its port-level visibility to internal
            sig = copy.copy(port)
            sig.vis = Visibility.INTERNAL
            sig.direction = PortDir.NONE
            return sig

        if isinstance(port, BundleInstance):
            # Copy the bundle, removing port and role fields.
            return BundleInstance(of=port.of, port=False, role=None)

        raise TypeError(f"Port {port}")

    def handle_noconn(self, module: Module, group: List[Union[PortRef, NoConn]]):
        """ Handle a group with a `NoConn`. """
        # First check for validity of the group, i.e. that the `NoConn` only connects to *one* port.
        if len(group) > 2:
            msg = f"Invalid multiply-connected `NoConn`, including {group} in {module}"
            raise RuntimeError(msg)
        # So `group` has two entries: a `NoConn` and a `PortRef`
        if isinstance(group[0], NoConn):
            return self.replace_noconn(module, portref=group[1], noconn=group[0])
        return self.replace_noconn(module, portref=group[0], noconn=group[1])

    def replace_noconn(self, module: Module, portref: PortRef, noconn: NoConn):
        """ Replace `noconn` with a newly minted `Signal`. """

        # Get the target Module's port-object corresponding to `portref`
        mod = portref.inst._resolved
        port = mod.ports.get(portref.portname, None)
        if port is None:
            msg = f"Invalid port connection to {portref} in {module}"
            raise RuntimeError(msg)

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
        portref.inst.conns[portref.portname] = sig


class SetList:
    """ A common combination of a hash-set and ordered list of the same items. 
    Used for keeping ordered items while maintaining quick membership testing. 
    
    FIXME: don't think the elaborator actually needs this any more, seems it could be a set only. """

    def __init__(self):
        self.set = set()
        self.list = list()

    def __contains__(self, item):
        return item in self.set

    def add(self, item):
        if item not in self.set:
            self.set.add(item)
            self.list.append(item)

    @property
    def order(self):
        return self.list
