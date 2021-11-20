"""
# hdl21 Elaboration 

Defines the primary `elaborate` method used to flesh out an in-memory `Module` or `Generator`. 
Internally defines and uses a number of hierarchical visitor-classes which traverse the hardware hierarchy, 
performing one or more transformation-passes.  
"""

# Std-Lib Imports
import copy
from enum import Enum
from types import SimpleNamespace
from typing import Union, Any, Dict, List, Optional, Tuple

# PyPi
from pydantic.dataclasses import dataclass

# Local imports
from .connect import connectable
from .module import Module, ExternalModuleCall
from .instance import InstArray, Instance, PortRef
from .primitives import R, PrimitiveCall
from .bundle import AnonymousBundle, Bundle, BundleInstance, _check_compatible
from .signal import PortDir, Signal, Visibility, Slice, Concat, Sliceable, NoConn
from .generator import Generator, GeneratorCall
from .params import _unique_name
from .instantiable import Instantiable


class Context:
    """Elaboration Context"""

    ...  # To be continued!


# Type short-hand for elaborate-able types
Elabable = Union[Module, GeneratorCall]
# (Plural Version)
Elabables = Union[Elabable, List[Elabable], SimpleNamespace]


def elabable(obj: Any) -> bool:
    # Function to test this, since `isinstance` doesn't work for `Union`.
    return isinstance(obj, (Module, Generator, GeneratorCall))


class _Elaborator:
    """ Base Elaborator Class """

    @classmethod
    def elaborate(cls, top, ctx):
        """ Elaboration entry-point. Elaborate the top-level object. """
        return cls(top, ctx).elaborate_top()

    def __init__(self, top: Elabable, ctx: Context):
        self.top = top
        self.ctx = ctx

    def elaborate_top(self):
        """ Elaborate our top node """
        if not isinstance(self.top, Module):
            raise TypeError
        return self.elaborate_module(self.top)

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """ Elaborate a GeneratorCall """
        # Only the generator-elaborator can handle generator calls; default it to error on others.
        raise RuntimeError(f"Invalid call to elaborate GeneratorCall by {self}")

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate a Module """
        # Required for all passes. Defaults to `NotImplementedError`.
        raise NotImplementedError

    def elaborate_external_module(self, call: ExternalModuleCall) -> ExternalModuleCall:
        """ Elaborate an ExternalModuleCall """
        # Default: nothing to see here, carry on
        return call

    def elaborate_primitive_call(self, call: PrimitiveCall) -> PrimitiveCall:
        """ Elaborate a PrimitiveCall """
        # Default: nothing to see here, carry on
        return call

    def elaborate_bundle_instance(self, inst: BundleInstance) -> None:
        """ Elaborate an BundleInstance """
        # Annotate each BundleInstance so that its pre-elaboration `PortRef` magic is disabled.
        inst._elaborated = True

    def elaborate_bundle(self, bundle: Bundle) -> Bundle:
        """ Elaborate an Bundle """
        # Default: nothing to see here, carry on
        return bundle

    def elaborate_instance_array(self, array: InstArray) -> Instantiable:
        """ Elaborate an InstArray """
        # Turn off `PortRef` magic
        array._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(array._resolved)

    def elaborate_instance(self, inst: Instance) -> Instantiable:
        """ Elaborate a Module Instance. """
        # This version of `elaborate_instantiable` is the "post-generators" version used by *most* passes.
        # The Generator-elaborator is different, and overrides it.

        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(inst._resolved)

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        # This version of `elaborate_instantiable` is the "post-generators" version used by *most* passes.
        # The Generator-elaborator is different, and overrides it.
        if not of:
            raise RuntimeError(f"Error elaborating undefined Instance-target {of}")
        if isinstance(of, Module):
            return self.elaborate_module(of)
        if isinstance(of, PrimitiveCall):
            return self.elaborate_primitive_call(of)
        if isinstance(of, ExternalModuleCall):
            return self.elaborate_external_module(of)
        raise TypeError

    @staticmethod
    def flatname(
        segments: List[str], *, avoid: Optional[Dict] = None, maxlen: int = 511
    ) -> str:
        """ Create a attribute-name merging string-list `segments`, while avoiding all keys in dictionary `avoid`.
        Commonly re-used while flattening  nested objects and while creating explicit attributes from implicit ones. 
        Raises a `RunTimeError` if no such name can be found of length less than `maxlen`. 
        The default max-length is 511 characters, a value representative of typical limits in target EDA formats. """

        if avoid is None:
            avoid = {}

        # The default format and result is of the form "seg0_seg1".
        # If that is in the avoid-keys, append underscores until it's not, or fails.
        name = "_".join(segments)
        while True:
            if len(name) > maxlen:
                msg = f"Could not generate a flattened name for {segments}: (trying {name})"
                raise RuntimeError(msg)
            if name not in avoid:  # Done!
                break
            name += "_"  # Collision; append underscore
        return name


class GeneratorElaborator(_Elaborator):
    """ Hierarchical Generator Elaborator
    Walks a hierarchy from `top` calling Generators. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator_calls = dict()  # GeneratorCalls to their (Module) results
        self.modules = dict()  # Module ids to references
        self.primitive_calls = dict()  # PrimitiveCall ids to references
        self.ext_module_calls = dict()  # PrimitiveCall ids to references

    def elaborate_top(self):
        """ Elaborate our top node """
        if isinstance(self.top, Module):
            return self.elaborate_module(self.top)
        if isinstance(self.top, GeneratorCall):
            return self.elaborate_generator_call(self.top)
        msg = f"Invalid Elaboration top-level {self.top}, must be a Module or Generator"
        raise TypeError(msg)

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """ Elaborate Generator-function-call `call`. Returns the generated Module. """

        # First check out cache
        if call in self.generator_calls:  # Already done!
            # Give the `call` a reference to its result.
            # Note this *has not* necessarily already happened, as the `self.generator_calls` key may be an equally-valued (but distinct) `GeneratorCall`.
            result = self.generator_calls[call]
            call.result = result
            return result

        # The main event: Run the generator-function
        if call.gen.usecontext:
            m = call.gen.func(call.arg, self.ctx)
        else:
            m = call.gen.func(call.arg)

        # Type-check the result
        # Generators may return other (potentially nested) generator-calls; unwind any of them
        while isinstance(m, GeneratorCall):
            # Note this should hit Python's recursive stack-check if it doesn't terminate
            m = self.elaborate_generator_call(m)
        # Ultimately they've gotta resolve to Modules, or they fail.
        if not isinstance(m, Module):
            msg = f"Generator {call.gen.func.__name__} returned {type(m)}, must return Module."
            raise TypeError(msg)

        # Give the GeneratorCall a reference to its result, and store it in our local dict
        call.result = m
        self.generator_calls[call] = m
        # Create a unique name
        # If the Module that comes back is anonymous, start by giving it a name equal to the Generator's
        if m.name is None:
            m.name = call.gen.func.__name__
        # Then add a unique suffix per its parameter-values
        m.name += "(" + _unique_name(call.arg) + ")"
        # Update the Module's `pymodule`, which generally at this point is `hdl21.generator`
        m._pymodule = call.gen.pymodule
        # And elaborate the module
        return self.elaborate_module(m)

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. 
        Primarily performs flattening of Instance Arrays, 
        and re-connecting to the resultant flattened instances  """
        if id(module) in self.modules:  # Already done!
            return module

        if not module.name:
            msg = f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            raise RuntimeError(msg)

        # Flatten Instance arrays
        while module.instarrays:
            name, array = module.instarrays.popitem()
            module.namespace.pop(name)
            # Visit the array's target
            target = self.elaborate_instance_array(array)

            # And do the real work: flattening it.
            if array.n < 1:
                raise RuntimeError(f"Invalid InstArray {array} with size {array.n}")
            # Create the new, flat Instances
            new_insts = []
            for k in range(array.n):
                name = self.flatname(
                    segments=[array.name, str(k)], avoid=module.namespace
                )
                inst = module.add(Instance(of=target, name=name))
                new_insts.append(inst)
            # And connect them
            for portname, conn in array.conns.items():
                if isinstance(conn, BundleInstance):
                    # All new instances get the same BundleInstance
                    for inst in new_insts:
                        inst.connect(portname, conn)
                elif isinstance(conn, (Signal, Slice, Concat)):
                    # Get the target-module port, particularly for its width
                    port = target.get(portname)
                    if not isinstance(port, Signal):
                        msg = f"Invalid port connection of `{portname}` {port} to {conn} in InstArray {array}"
                        raise RuntimeError(msg)

                    if port.width == conn.width:
                        # All new instances get the same signal
                        for inst in new_insts:
                            inst.connect(portname, conn)
                    elif port.width * array.n == conn.width:
                        # Each new instance gets a slice, equal to its own width
                        for k, inst in enumerate(new_insts):
                            slize = conn[k * port.width : (k + 1) * port.width]
                            if slize.width != port.width:
                                msg = f"Width mismatch connecting {slize} to {port}"
                                raise RuntimeError(msg)
                            inst.connect(portname, slize)
                    else:  # All other width-values are invalid
                        msg = f"Invalid connection of {conn} of width {conn.width} to port {portname} on Array {array.name} of width {port.width}. "
                        msg += f"Valid widths are either {port.width} (broadcasting across instances) and {port.width * array.n} (individually wiring to each)."
                        raise RuntimeError(msg)
                else:
                    msg = f"Invalid connection to {conn} in InstArray {array}"
                    raise TypeError(msg)

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        # Also visit bundle instances, turning off their pre-elab magic
        for bundle in module.bundles.values():
            self.elaborate_bundle_instance(bundle)

        # Store a reference to the now-expanded Module in our cache, and return it
        self.modules[id(module)] = module
        return module

    def elaborate_instance(self, inst: Instance) -> Instantiable:
        """ Elaborate a Module Instance. """
        # This version differs from `Elaborator` in operating on the *unresolved* attribute `inst.of`,
        # instead of the resolved version `inst._resolved`.

        # Turn off `PortRef` magic
        inst._elaborated = True
        # And visit the Instance's target
        return self.elaborate_instantiable(inst.of)

    def elaborate_instantiable(self, of: Instantiable) -> Instantiable:
        """ Elaborate an Instance target. Adds the capacity to call `GeneratorCall`s to the more-common base-case. """
        if isinstance(of, GeneratorCall):
            return self.elaborate_generator_call(call=of)
        return super().elaborate_instantiable(of)


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

        # Now work through expanding any implicit-ish connections, such as those from port to port.
        # Start by building an adjacency graph of every `PortRef` and `NoConn` that's been instantiated.
        portconns = dict()
        for inst in module.instances.values():
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
            for inst in module.instances.values():
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
                    raise RuntimeError(
                        f"Port {portref.portname} not found in Bundle {bundle_inst.of.name}"
                    )
                # Walk through our Instances, replacing any connections to this `PortRef` with `flatsig`
                for inst in module.instances.values():
                    for portname, conn in inst.conns.items():
                        if conn is portref:
                            inst.conns[portname] = flatsig

        # Go through each Instance, replacing `AnonymousBundle`s with their referents
        for inst in module.instances.values():
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
                        raise RuntimeError
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

        # And then check each Instance
        for inst in module.instances.values():
            self.check_instance(module, inst)

        # No errors means it checked out, return the Module unchanged
        return module

    def check_instance(self, module: Module, inst: Instance) -> None:
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


class Orphanage(_Elaborator):
    """ # Orphan-Checking Elaborator Pass 

    Ensures each Module-attribute is "parented" by the `Module` which holds it. 
    Errant cases can come up for code such as: 
    
    ```
    m1 = h.Module(name='m1')
    m1.s = h.Signal() # Signal `s` is now "parented" by `m1`

    m2 = h.Module(name='m2')
    m2.y = m1.s # Now `s` has been "orphaned" (or perhaps "cradle-robbed") by `m2`
    ```

    This essentially boils down to the difference between Python's native reference-semantics, 
    and `hdl21.Module`'s notion of "owning" its attributes. 
    Note other *references* to Module attributes are allowed, such as: 

    ```
    m1 = h.Module(name='m1')
    m1.s = h.Signal() # Signal `s` is now "parented" by `m1`

    my_favorite_signals = { "from_m1" : m1.s }
    ```

    Here the dictionary `my_favorite_signals` retains a reference to Signal `s`. 
    This does not generate an orphan-error complaint, so long as Module-level ownership is unique and unambiguous. 

    The orphan-test is very simple: each Module-attribute is annotated with a `_parent_module` member 
    upon insertion into the Module namespace. 
    Orphan-testing simply requires that for each attribute, this member is identical to the parent Module. 
    A `RuntimeError` is raised if orphaned attributes are detected. 
    Otherwise each Module is returned unchanged.
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate a Module """
        # Check each attribute in the module namespace for orphanage.
        for attr in module.namespace.values():
            if attr._parent_module is not module:
                msg = f"Orphanage: Module {module} attribute {attr} is actually owned by another Module {attr._parent_module}!"
                raise RuntimeError(msg)
        # Checks out! Return the module unchanged.
        return module


class SliceResolver(_Elaborator):
    """ Elaboration pass to resolve slices and concatenations to concrete signals. 
    Modifies connections to any nested slices, nested concatenations, or combinations thereof. 
    "Full-width" `Slice`s e.g. `sig[:]` are replaced with their parent `Signal`s.

    TODO: `Slice`s with non-unit `step` are converted to `Concat`s. """

    def elaborate_module(self, module: Module) -> Module:
        # Depth-first traverse instances, covering their targets first.
        for inst in module.instances.values():
            self.elaborate_instance(inst)

        # Then do the real work, updating any necessary connections on each instance
        for inst in module.instances.values():
            self.update_instance(module, inst)

        return module

    def update_instance(self, module: Module, inst: Instance) -> None:
        """ Update all `Slice` and `Concat` valued connections to remove nested `Slice`s """

        for portname, conn in inst.conns.items():
            if isinstance(conn, (Slice, Concat)):
                inst.conns[portname] = _resolve_sliceable(conn)
            # All other connection-types (Signals, Interfaces) are fine


def _resolve_sliceable(conn: Sliceable) -> Sliceable:
    """ Resolve a `Sliceable` to flat-concatenation-amenable elements. """
    if isinstance(conn, Signal):
        return conn  # Nothing to do
    if isinstance(conn, Slice):
        return _resolve_slice(conn)
    if isinstance(conn, Concat):
        return _resolve_concat(conn)
    raise TypeError(f"Invalid attempt to resolve slicing on {conn}")


def _list_slice(slize: Slice) -> List[Slice]:
    """ Internal recursive helper for `resolve_slice`. 
    Returns a list of Slices in which each element has a concrete Signal for its parent. """

    # Resolve "full-width" slices to their parent Signals
    if slize.width == slize.signal.width:
        # Return a single-element list, after resolution
        return [_resolve_sliceable(slize.signal)]

    if isinstance(slize.signal, Signal):
        return [slize]  # Already all good! Just make a one-element list.

    # Do some actual work. Recursively peel off a bit at a time.
    if slize.width == 1:
        # Base case: slice is one-bit wide. Reach into the parent signal and grab that bit.

        if isinstance(slize.signal, Slice):
            parent = slize.signal  # Note this is also a Slice
            return _list_slice(parent.signal[parent.bot + slize.bot])

        if isinstance(slize.signal, Concat):
            idx = 0  # Find the `part` including our index
            for part in slize.signal.parts:
                if part.width + idx > slize.bot:
                    return _list_slice(part[slize.bot - idx])
                idx += part.width
            msg = f"Slice {slize} is out of bounds of Concat {slize.signal}"
            raise RuntimeError(msg)

        raise TypeError(f"Invalid attempt to resolve slicing on {slize}")

    # Otherwise recurse in something like a "cons" pattern, splitting between the first bit and the rest.

    if slize.step is not None and slize.step < 0:  # Negative step, begin from `top`
        first = _list_slice(slize.signal[slize.top])
        rest = slize.signal[slize.top + slize.step : slize.bot : slize.step]
        rest = _list_slice(rest)

    else:  # Positive step, begin from `bot`
        step = slize.step if slize.step is not None else 1
        first = _list_slice(slize.signal[slize.bot])
        rest = _list_slice(slize.signal[slize.bot + step : slize.top : slize.step])

    return first + rest


def _resolve_slice(slize: Slice) -> Sliceable:
    """ Resolve a `Slice` to one or more with "concrete" `Signal`s as parents. 
    
    Slices of other Slices and Slices of Concats are both valid design-time constructions. 
    For example: 
    ```python
    h.Concat(sig1, sig2, sig3)[1] # Slice of a Concat
    sig4[0:2][1] # Slice of a Slice
    ```

    While these may not frequently be created by designers, they are (at least) often created by array broadcasting. 
    As some point their parents must be resolved to their original Signals, at minimum before export-level name resolution. 

    Resolving Concatenations can generally resolve to more than one Slice, as in: 
    ```python
    h.Concat(sig1[0], sig2[0], sig3[0])[0:1] # Requires slices of `sig1` and `sig2`
    ``` 
    Such cases create and return a Concatenation. """

    # Break out the slice elements in a list
    ls = _list_slice(slize)
    # And convert to either a single element or Concat
    if len(ls) == 1:  # Resolved to single Slice
        return ls[0]
    elif len(ls) > 1:  # Multiple parts required - concatenate them
        return Concat(*ls)

    raise RuntimeError(f"Error resolving Slice {slize}")


def _resolve_concat(conc: Concat) -> Concat:
    """ Resolve a Concatenation into (a) concrete Signals and (b) Slices of concrete Signals. 
    Removes nested concatenations and resolves slices along the way. """

    if not len(conc.parts):
        raise RuntimeError("Concatenation with no parts")

    if all(_flat_concatable(p) for p in conc.parts):
        return Concat(*[_resolve_sliceable(p) for p in conc.parts])

    if isinstance(conc.parts[0], Concat):
        # Recursively cover the first element, and all others
        first = _resolve_concat(conc.parts[0])
        rest = _resolve_concat(Concat(*conc.parts[1:]))
        return Concat(*(first.parts + rest.parts))

    if isinstance(conc.parts[0], Slice):
        # Resolve everything within the Slice to a list of concrete-Signal slices
        first = _resolve_slice(conc.parts[0])
        # Pass everything else recursively back to this method
        rest = _resolve_concat(Concat(*conc.parts[1:]))
        # And concatenate the two
        return Concat(*(first + rest.parts))

    # Otherwise peel off as many Signals and concrete-Signal Slices as we can
    for idx in range(len(conc.parts)):
        if _flat_concatable(conc.parts[idx]):
            continue
        # Hit our first "compound" entry. Split the list here.
        first = conc.parts[:idx]
        rest = _resolve_concat(Concat(*conc.parts[idx:]))
        return Concat(*(first + rest.parts))

    raise RuntimeError("Unable to resolve concatenation")


def _flat_concatable(s: Sliceable) -> bool:
    """ Boolean indication of whether `s` is suitable for flattened Concatenations. 
    Such objects must be either: 
    * (a) A Signal, or
    * (b) A Slice into a Signal
    Notable exceptions include Concats and nested Slices of Concats and other Slices. """
    return isinstance(s, Signal) or (
        isinstance(s, Slice) and isinstance(s.signal, Signal)
    )


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


class ElabPass(Enum):
    """ Enumerated Elaborator Passes
    Each has a `value` attribute which is an Elaborator-pass, 
    and a `name` attribute which is a (Python-enum-style) capitalized name. 
    Specifying  """

    RUN_GENERATORS = GeneratorElaborator
    ORPHANAGE = Orphanage
    IMPLICIT_BUNDLES = ImplicitBundles
    BUNDLE_CONN_TYPES = BundleConnTypes
    FLATTEN_BUNDLES = BundleFlattener
    IMPLICIT_SIGNALS = ImplicitSignals
    SIGNAL_CONN_TYPES = SignalConnTypes
    RESOLVE_SLICES = SliceResolver

    @classmethod
    def default(cls) -> List["ElabPass"]:
        """ Return the default ordered Elaborator Passes. """
        # Returns each in definition order, then a final `Orphanage` test.
        return list(ElabPass) + [ElabPass.ORPHANAGE]


def elab_all(top: Elabables, **kwargs) -> List[Elabable]:
    """ Elaborate everything we can find - potentially recursively - in `Elabables` `top`. 

    Results are returned in a list, not necessarily reproducing the structure of `top`. 
    Note the *attributes* of `top` are also generally modified in-place, allowing access to their elaboration results. """
    # Recursively create a list of all elab-able types in `obj`
    ls = []
    _list_elabables_helper(top, ls)
    # Elaborate each, and return them as a list
    return [elaborate(top=t, **kwargs) for t in ls]


def _list_elabables_helper(obj: Any, accum: list) -> None:
    """ Recursive helper for hierarchically finding elaborate-able things in `obj`. 
    Newly-found items are appended to accumulation-list `accum`. """
    if elabable(obj):
        accum.append(obj)
    elif isinstance(obj, list):
        [_list_elabables_helper(i, accum) for i in obj]
    elif isinstance(obj, SimpleNamespace):
        # Note this skips over non-elaboratable items (e.g. names), where the list demands all be suitable.
        for i in obj.__dict__.values():
            if isinstance(i, (SimpleNamespace, list)) or elabable(i):
                _list_elabables_helper(i, accum)
    else:
        raise TypeError(f"Attempting Invalid Elaboration of {obj}")


def elaborate(
    top: Elabable,
    *,
    ctx: Optional[Context] = None,
    passes: Optional[List[ElabPass]] = None,
) -> Module:
    """ In-Memory Elaboration of Generator or Module `top`. 
    
    Optional `passes` lists the ordered `ElabPass`es to run. By default it runs the order specified by `ElabPass.default`. 
    Note the order of passes is important; many depend upon others to have completed before they can successfully run. 

    Optional `Context` field `ctx` is not yet supported. 

    `elaborate` executes elaboration of a *single* `top` object. 
    For (plural) combinations of `Elabable` objects, use `elab_all`. 
    """
    # Expand default values
    ctx = ctx or Context()
    passes = passes or ElabPass.default()

    # Pass `top` through each of our passes, in order
    res = top
    for pass_ in passes:
        res = pass_.value.elaborate(top=res, ctx=ctx)
    return res
