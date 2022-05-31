""" 
# Elaborator Class(es)

Recursive walkers of Hdl21 hierarchies which perform the mechanics of elaboration. 
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


class ImplicitSignals(_Elaborator):
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

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_array(arr)

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


@dataclass
class Path:
    """ Hierarchical String-Valued Path """

    segs: List[str]  # List of path segments

    @classmethod
    def concat(cls, prefix: str, suffix: "Path") -> "Path":
        return cls([prefix] + suffix.segs[:])

    def to_name(self) -> str:
        return "_".join(self.segs)


# The path-separator used in PathStrings.
# Hopefully never actually used in a real name.
_MAGIC_PATH_SEP = "~!@#$%^&*()"


@dataclass(frozen=True)
class PathStr:
    """ Single-String Representation of `Path` """

    val: str

    def to_path(self) -> Path:
        return Path(self.val.split(_MAGIC_PATH_SEP))

    def to_name(self) -> str:
        return self.to_path().to_name()

    @classmethod
    def concat(cls, prefix: str, suffix: "PathStr") -> "PathStr":
        return cls(prefix + _MAGIC_PATH_SEP + suffix.val)

    @classmethod
    def from_path(cls, path: Path) -> "PathStr":
        s = _MAGIC_PATH_SEP.join(path.segs)
        return cls(s)

    @classmethod
    def from_list(cls, ls: List[str]) -> "PathStr":
        return cls.from_path(Path(ls))


@dataclass
class FlatBundleDef:
    """ Flattened Bundle Definition """

    # Source/ Original Bundle
    src: Bundle
    # Flattened signals-dict, keyed by Path
    signals: Dict[PathStr, Signal]


@dataclass
class FlatBundleInst:
    """ Flattened Bundle Instance """

    # Source/ Original Bundle
    src: BundleInstance
    # Flattened signals-dict, keyed by Path
    signals: Dict[PathStr, Signal]


class BundleFlattener(_Elaborator):
    """ Bundle-Flattening Elaborator Pass """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modules = dict()
        # Bundle (definition) replacements, id(Bundle) => FlatBundle
        self.bundle_defs: Dict[int, FlatBundleDef] = dict()
        # BundleInstance replacements, id(BundleInst) => FlatBundleInst
        self.bundle_insts: Dict[int, FlatBundleInst] = dict()
        # AnonymousBundle replacements, id(AnonBundle) => FlatBundleFlatBundleInst
        self.anon_replacements: Dict[int, FlatBundleInst] = dict()
        # Connection replacement-dicts, Module (id) => Connections Dict
        self.conn_replacements: Dict[int, Dict[str, FlatBundleInst]] = dict()
        # Replacement-values by Module and attribute-name.
        self.module_attrs: Dict[
            Tuple[int, str], Tuple[BundleInstance, FlatBundleInst]
        ] = dict()

    def elaborate_module(self, module: Module) -> Module:
        """ Flatten Module `module`s Bundles, replacing them with newly-created Signals.
        Reconnect the flattened Signals to any Instances connected to said Bundles. """

        if id(module) in self.modules:
            return module  # Already done!

        # Depth-first traverse our instances first.
        # After this loop, each Instance's Module can have newly-expanded ports -
        # but *will not* have modified its `conns` dict.
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_array(arr)

        # Start a dictionary of bundle-conn_replacements
        conn_replacements: Dict[str, FlatBundleInst] = dict()

        while module.bundles:
            # Remove the bundle-instance from the module
            name, bundle_inst = module.bundles.popitem()
            module.namespace.pop(name)
            # Check we haven't (somehow) already flattened it
            if id(bundle_inst) in self.bundle_insts:
                msg = f"Bundle Instance {bundle_inst} in Module {module} flattened more than once. Was it actually part of another Module?"
                raise RuntimeError(msg)
            # Flatten it
            flat = self.flatten_bundle_inst(bundle_inst)
            # And store the result
            self.bundle_insts[id(bundle_inst)] = flat
            self.module_attrs[(id(module), name)] = (bundle_inst, flat)
            conn_replacements[name] = flat

            # Add each flattened Signal. Note flattened Signals are modified in-place.
            for pathstr, sig in flat.signals.items():
                # Rename the signal, prepending the bundle-instance's name
                # path = Path.concat(bundle_inst.name, pathstr.to_path())
                sig.name = self.flatname(
                    segments=[bundle_inst.name, pathstr.to_name()],
                    avoid=module.namespace,
                )
                # Sort out the new Signal's visibility and direction
                if bundle_inst.port:
                    vis_ = Visibility.PORT
                    if bundle_inst.role is None:
                        dir_ = PortDir.NONE
                    elif bundle_inst.role == sig.src:
                        dir_ = PortDir.OUTPUT
                    elif bundle_inst.role == sig.dest:
                        dir_ = PortDir.INPUT
                    else:
                        dir_ = PortDir.NONE
                else:
                    vis_ = Visibility.INTERNAL
                    dir_ = PortDir.NONE
                # Apply all these attributes to our new Signal
                sig.vis = vis_
                sig.direction = dir_
                # And add it to the Module namespace
                module.add(sig)

            # Replace connections to any connected instances
            # FIXME: a better word for "instances or arrays thereof"; we already used "connectable"
            connectables = list(module.instances.values()) + list(
                module.instarrays.values()
            )
            for inst in connectables:
                for portname in list(inst.conns.keys()):
                    # Operate on connections to *this* bundle instance
                    if inst.conns[portname] is bundle_inst:
                        t = self.module_attrs.get((id(inst._resolved), portname), None)
                        if t is None:
                            msg = f"Invalid Port Connection to {portname} on Instance {inst} in Module {module}"
                            raise RuntimeError(msg)
                        # Destructure the hierarchical and flat versions that come back
                        _hier_bundle_port, flat_bundle_port = t
                        # Replace the connection to each flattened Signal
                        for pathstr, flat_port in flat_bundle_port.signals.items():
                            # Note `flat_port.name` will be `inst`'s name, i.e. `_mybus_clk_`
                            # Whereas its `path` will line up to `flat`'s namespace, i.e. `['bus']`
                            inst.conns[flat_port.name] = flat.signals[pathstr]
                        inst.conns.pop(portname)

            # Re-connect any PortRefs that `bundle` has given out, as in the form:
            # i = SomeBundle()       # Theoretical Bundle with signal-attribute `s`
            # x = SomeModule(s=i.s)  # Connects `PortRef` `i.s`
            # FIXME: this needs to happen for hierarchical bundles too
            for portref in bundle_inst.portrefs.values():
                flatsig = flat.signals.get(PathStr(portref.portname), None)
                if flatsig is None:
                    msg = f"Port {portref.portname} not found in Bundle {bundle_inst.of.name}"
                    raise RuntimeError(msg)
                # Walk through our Instances, replacing any connections to this `PortRef` with `flatsig`
                # FIXME: a better word for "instances or arrays thereof"; we already used "connectable"
                connectables = list(module.instances.values()) + list(
                    module.instarrays.values()
                )
                for inst in connectables:
                    for portname, conn in inst.conns.items():
                        if conn is portref:
                            inst.conns[portname] = flatsig

        # Go through each Instance, replacing `AnonymousBundle`s with their referents
        # FIXME: a better word for "instances or arrays thereof"; we already used "connectable"
        connectables = list(module.instances.values()) + list(
            module.instarrays.values()
        )
        for inst in connectables:
            for portname in list(inst.conns.keys()):
                conn = inst.conns[portname]
                if isinstance(conn, AnonymousBundle):
                    # FIXME: hierarchical `AnonymousBundle`s are not handled here
                    if len(conn.bundles):
                        raise NotImplementedError(f"Nested AnonymousBundle")
                    # `module.portname` must be in our `module_attrs` by now (or fail)
                    t = self.module_attrs.get((id(inst._resolved), portname), None)
                    if t is None:
                        msg = f"Invalid Port Connection to {portname} on Instance {inst} in Module {module}"
                        raise RuntimeError(msg)
                    # Destructure the hierarchical and flat versions that come back
                    _hier_bundle_port, flat_bundle_port = t
                    # Replace the connection to each flattened Signal
                    for pathstr, flat_port in flat_bundle_port.signals.items():
                        # Note `flat_port.name` will be `inst`'s name, i.e. `_mybus_clk_`
                        # Whereas its `path` will line up to `flat`'s namespace, i.e. `['bus']`
                        inst.conns[flat_port.name] = conn.signals[pathstr.val]
                    inst.conns.pop(portname)

        # Store results in our cache
        self.modules[id(module)] = module
        self.conn_replacements[id(module)] = conn_replacements
        return module

    def flatten_bundle_def(self, bundle: Bundle) -> FlatBundleDef:
        """ Flatten a `Bundle` (definition). 
        Note Signals *are not* copied upon `FlatBundleDef` creation, 
        but must be while unrolling to each `FlatBundleInst`. """

        if id(bundle) in self.bundle_defs:
            return self.bundle_defs[id(bundle)]  # Already done!

        # Create the flattened version, initializing it with `bundle`s scalar Signals,
        # Converting their keys to `Path` elements
        flat = FlatBundleDef(
            src=bundle,
            signals={
                PathStr.from_list([sig.name]): sig for sig in bundle.signals.values()
            },
        )
        # Depth-first walk any bundle-instance's definitions, flattening them
        for i in bundle.bundles.values():
            iflat = self.flatten_bundle_def(i.of)
            for path_suffix, sig in iflat.signals.items():
                # Pre-pend the bundle name to its path, and add to our Signals-dict
                pathstr = PathStr.concat(i.name, path_suffix)
                if pathstr in flat.signals:
                    raise RuntimeError(
                        f"Error Flattening {bundle}: colliding flattened Signal names for {sig} and {flat.signals[pathstr]}"
                    )
                flat.signals[pathstr] = sig

        # Store it in our cache, and return
        self.bundle_defs[id(bundle)] = flat
        return flat

    def flatten_bundle_inst(self, bundle: BundleInstance) -> FlatBundleInst:
        """ Convert nested Bundle `bundle` into a flattened `FlatBundleInst` of scalar Signals. 
        Signals are copied in the creation of each `BundleInstance`, so no further copying is required at the Module-level. """

        # Get the (flattened) Bundle-definition
        flatdef = self.flatten_bundle_def(bundle.of)

        # Copy and rename its signals
        signals = dict()
        for pathstr, sig in flatdef.signals.items():
            sig = copy.deepcopy(sig)
            sig.name = pathstr.to_name()
            signals[pathstr] = sig

        # And return a new `FlatBundleInst`
        return FlatBundleInst(src=bundle, signals=signals)

    def flatten_anonymous_bundle(self, bundle: AnonymousBundle) -> FlatBundleInst:
        """ Flatten an `AnonymousBundle`. 
        Differs from bundle-class instances in that each attribute of anonymous-bundles 
        are generally "references", owned by something else, commonly a Module. """

        raise NotImplementedError

        # Create the flattened version, initializing it with `bundle`s scalar Signals
        flat = FlatBundleInst(
            inst_name=bundle.name,
            src=bundle.of,
            signals=copy.deepcopy(bundle.of.signals),
        )
        # Depth-first walk any bundle-instance's definitions, flattening them
        for i in bundle.of.bundles.values():
            iflat = self.flatten_bundle(i)
            for sig in iflat.signals.values():
                # Rename the signal, and store it in our flat-bundle
                signame = self.flatname([i.name, sig.name], avoid=flat.signals)
                sig.name = signame
                flat.signals[signame] = sig
        return flat


class ImplicitBundles(_Elaborator):
    """ Create explicit `BundleInstance`s for any implicit ones, 
    i.e. those created through port-to-port connections. """

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. First depth-first elaborates its Instances,
        before creating any implicit `BundleInstance`s and connecting them. """

        # FIXME: much of this can and should be shared with `ImplicitSignals`

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_array(arr)

        # Now work through expanding any implicit-ish connections, such as those from port to port.
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
                        raise RuntimeError(
                            f"Invalid connection to {portconn}, shorting {[(p.inst.name, p.portname) for p in net]}"
                        )
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
                    raise RuntimeError(
                        f"Invalid port {portref.portname} on Instance {portref.inst.name} in Module {module.name}"
                    )
                # Rename it and add it to the Module namespace
                sig.name = signame
                module.add(sig)
            # And re-connect it to each Instance
            for portref in net:
                portref.inst.conns[portref.portname] = sig

        return module


class BundleConnTypes(_Elaborator):
    """ Check for connection-type-validity on each Bundle-valued connection. 
    Note this stage *does not* perform port-direction checking or modification. 
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Check each Instance's connections in `module` """

        # Depth-first traverse instances, checking them first.
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        for arr in module.instarrays.values():
            self.elaborate_instance_array(arr)

        # And then check each Instance
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



class SignalConnTypes(_Elaborator):
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

        # Depth-first traverse instances, checking them first.
        for inst in module.instances.values():
            self.elaborate_instance(inst)

        # And then check each Instance
        for inst in module.instances.values():
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
