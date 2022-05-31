"""
# PortRef Resolution 

Creates concrete `Signal`s and `BundleInstance`s to replace `PortRef`s.
"""

# Std-Lib Imports
import copy
from typing import Union, Dict, List, Optional

# Local imports
from ...module import Module
from ...instance import PortRef
from ...bundle import Bundle, BundleInstance
from ...signal import PortDir, Signal, Visibility, NoConn

# Import the base class
from .base import Elaborator


class ImplicitSignals(Elaborator):
    """ Explicitly create any implicitly-defined `Signal`s, 
    e.g. those defined by port-to-port connections. """

    def elaborate_module(self, module: Module) -> Module:
        """Elaborate Module `module`. First depth-first elaborates its Instances,
        before creating any implicit Signals and connecting them."""

        # FIXME: much of this can and should be shared with `ImplicitBundles`

        # Bundles must be flattened before this point. Throw an error if not.
        if len(module.bundles):
            msg = f"ImplicitSignals elaborator invalidly invoked on Module {module} with Bundles {module.bundles}"
            raise RuntimeError(msg)

        # Now work through expanding any implicit-ish connections, such as those from port to port.
        # Start by building an adjacency graph of every `PortRef` and `NoConn` that's been instantiated.
        portconns: Dict[PortRef, PortRef] = dict()
        # FIXME: a better word for "instances or arrays thereof"; we already used "connectable"
        connectables = list(module.instances.values()) + list(
            module.instarrays.values()
        )
        for inst in connectables:
            for port, conn in inst.conns.items():
                if isinstance(conn, (PortRef, NoConn)):
                    internal_ref = PortRef.new(inst, port)
                    portconns[internal_ref] = conn

        # Create and connect Signals for each `NoConn` and `PortRef`
        self.replace_portconns(module, portconns)

        return module

    def replace_portconns(
        self, module: Module, portconns: Dict[PortRef, PortRef]
    ) -> Module:
        """ Replace each port-to-port connection in `portconns` with concrete `Signal`s. """

        # Now walk through all port-connections, assigning each set to a net
        nets: List[List[Union[PortRef, NoConn]]] = list()

        while portconns:
            # Keep both a list for consistent ordering, and a set for quick membership tests
            this_net = SetList()
            # Grab a random pair
            inner, outer = portconns.popitem()
            this_net.add(inner)
            this_net.add(outer)
            # If it's connected to others, grab those
            while outer in portconns:
                outer = portconns.pop(outer)
                this_net.add(outer)
            # Once we find an object not in `portconns`, we've covered everything connected to the net.
            nets.append(this_net.order)

        # For each net, find and/or create a Signal to replace all the PortRefs with.
        for net in nets:
            self.handle_net(module, net)

        return module

    def handle_net(self, module: Module, net: List[Union[PortRef, NoConn]]):
        """ Handle a `net` worth of connected Ports and NoConns """

        # First cover `NoConn` connections, checking for any invalid multiple-conns to them.
        if any([isinstance(n, NoConn) for n in net]):
            return self.handle_noconn(module, net)
        return self.handle_portconn(module, net)

    def handle_portconn(self, module: Module, net: List[PortRef]):
        """ Handle re-connecting a list of connected `PortRef`s. 
        Creates and adds a fresh new `Signal` if one does not already exist. """

        # Find any existing, declared `Signal` connected to `net`.
        sig = self.find_signal(net)

        # If we didn't find any, go about naming and creating one
        if sig is None:
            sig = self.create_signal(module, net)

        # And re-connect it to each Instance
        for portref in net:
            portref.inst.conns[portref.portname] = sig

    def find_signal(self, net: List[PortRef]) -> Optional[Signal]:
        """ Find any existing, declared `Signal` connected to `net`. 
        And if there are any, make sure there's only one. 
        Returns `None` if no `Signal`s present. """
        sig = None
        for portref in net:
            portconn = portref.inst.conns.get(portref.portname, None)
            if isinstance(portconn, Signal):
                if sig is not None and portconn is not sig:
                    msg = f"Invalid connection to {portconn}, shorting {[(p.inst.name, p.portname) for p in net]}"
                    raise RuntimeError(msg)
                sig = portconn
        return sig

    def create_signal(self, module: Module, net: List[PortRef]) -> Signal:
        """ Create a new `Signal`, parametrized and named to connect to the `PortRef`s in `net`. """
        # Find a unique name for the new Signal.
        # The default name template is "_inst1_port1_inst2_port2_inst3_port3_"
        signame = self.flatname(
            segments=[f"{p.inst.name}_{p.portname}" for p in net],
            avoid=module.namespace,
        )
        # Create the Signal, looking up all its properties from the last Instance's Module
        # (If other instances are inconsistent, later stages will flag them)
        portref = net[-1]
        lastmod = portref.inst._resolved
        sig = lastmod.ports.get(portref.portname, None)
        if sig is None:  # Clone it, and remove any Port-attributes
            msg = f"Invalid port {portref.portname} on Instance {portref.inst.name} in Module {module.name}"
            raise RuntimeError(msg)

        # Make a copy, and update its port-level visibility to internal
        sig = copy.copy(sig)
        sig.vis = Visibility.INTERNAL
        sig.direction = PortDir.NONE

        # Rename it and add it to the Module namespace
        sig.name = signame
        module.add(sig)
        return sig

    def handle_noconn(self, module: Module, net: List[Union[PortRef, NoConn]]):
        """ Handle a net with a `NoConn`. """
        # First check for validity of the net, i.e. that the `NoConn` only connects to *one* port.
        if len(net) > 2:
            msg = f"Invalid multiply-connected `NoConn`, including {net} in {module}"
            raise RuntimeError(msg)
        # So `net` has two entries: a `NoConn` and a `PortRef`
        if isinstance(net[0], NoConn):
            return self.replace_noconn(module, portref=net[1], noconn=net[0])
        return self.replace_noconn(module, portref=net[0], noconn=net[1])

    def replace_noconn(self, module: Module, portref: PortRef, noconn: NoConn):
        """ Replace `noconn` with a newly minted `Signal`. """

        # Get the target Module's port-object corresponding to `portref`
        mod = portref.inst._resolved
        port = mod.ports.get(portref.portname, None)
        if port is None:
            msg = f"Invalid port connection to {portref} in {module}"
            raise RuntimeError(msg)

        # Copy any relevant attributes of the Port
        sig = copy.copy(port)
        # And set the new copy to internal-visibility
        sig.vis = Visibility.INTERNAL
        sig.direction = PortDir.NONE

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


class ImplicitBundles(Elaborator):
    """ Create explicit `BundleInstance`s for any implicit ones, 
    i.e. those created through port-to-port connections. """

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. First depth-first elaborates its Instances,
        before creating any implicit `BundleInstance`s and connecting them. """

        # FIXME: much of this can and should be shared with `ImplicitSignals`

        # Work through expanding any implicit-ish connections, such as those from port to port.
        # Start by building an adjacency graph of every bundle-valued `PortRef` that's been instantiated.
        portconns = dict()
        for inst in module.instances.values():
            for port, conn in inst.conns.items():
                if isinstance(conn, PortRef) and isinstance(
                    conn.inst._resolved, (Module, Bundle)
                ):
                    other_port = conn.inst._resolved.get(conn.portname)
                    if other_port is None:
                        msg = f"Cannot resolve connection to {port} on {inst}"
                        raise RuntimeError(msg)
                    if isinstance(other_port, BundleInstance):
                        internal_ref = PortRef.new(inst, port)
                        portconns[internal_ref] = conn

        # Now walk through them, assigning each set to a net
        nets: List[List[PortRef]] = list()
        while portconns:
            # Keep both a list for consistent ordering (we think), and a set for quick membership tests
            this_net = SetList()
            # Grab a random pair
            inner, outer = portconns.popitem()
            this_net.add(inner)
            this_net.add(outer)
            # If it's connected to others, grab those
            while outer in portconns:
                outer = portconns.pop(outer)
                this_net.add(outer)
            # Once we find an object not in `portconns`, we've covered everything connected to the net.
            nets.append(this_net.order)

        # For each net, find and/or create a Signal to replace all the PortRefs with.
        for net in nets:
            # Check whether any of them are connected to declared Signals.
            # And if any are, make sure there's only one
            sig = None
            for portref in net:
                portconn = portref.inst.conns.get(portref.portname, None)
                if isinstance(portconn, BundleInstance):
                    if sig is not None and portconn is not sig:
                        # Ruh roh! shorted between things
                        msg = f"Invalid connection to {portconn}, shorting {[(p.inst.name, p.portname) for p in net]}"
                        raise RuntimeError(msg)
                    sig = portconn
            # If we didn't find any, go about naming and creating one
            if sig is None:
                # Find a unique name for the new Signal.
                # The default name template is "_inst1_port1_inst2_port2_inst3_port3_"
                signame = self.flatname(
                    segments=[f"{p.inst.name}_{p.portname}" for p in net],
                    avoid=module.namespace,
                )
                # Create the Signal, looking up all its properties from the last Instance's Module
                # (If other instances are inconsistent, later stages will flag them)
                lastmod = portref.inst._resolved
                sig = lastmod.bundle_ports.get(portref.portname, None)
                if sig is not None:
                    # Copy the bundle, removing port and role fields.
                    sig = BundleInstance(
                        name=sig.name, of=sig.of, port=False, role=None,
                    )
                else:
                    msg = f"Invalid port {portref.portname} on Instance {portref.inst.name} in Module {module.name}"
                    raise RuntimeError(msg)
                # Rename it and add it to the Module namespace
                sig.name = signame
                module.add(sig)
            # And re-connect it to each Instance
            for portref in net:
                portref.inst.conns[portref.portname] = sig

        return module


class SetList:
    """ A common combination of a hash-set and ordered list of the same items. 
    Used for keeping ordered items while maintaining quick membership testing. """

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
