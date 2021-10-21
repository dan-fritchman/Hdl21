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
from .primitives import PrimitiveCall
from .bundle import AnonymousBundle, Bundle, BundleInstance, _check_compatible
from .signal import PortDir, Signal, Visibility
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
                elif isinstance(conn, Signal):
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
                            # FIXME: will be impacted by slice-indices changes!
                            slize = conn[k * port.width : (k + 1) * port.width - 1]
                            if slize.width != port.width:
                                msg = f"Width mismatch connecting {slize} to {port}"
                                raise RuntimeError(msg)
                            inst.connect(portname, slize)
                    else:  # All other values are invalid
                        msg = f"Invalid connection between {conn} of width {conn.width} and {array.n}"
                        raise RuntimeError(msg)
                elif isinstance(conn, (Slice, Concat)):
                    raise NotImplementedError  # COMING SOON!
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

        # Bundles must be flattened before this point.
        # Throw an error if not.
        if len(module.bundles):
            msg = f"ImplicitSignals elaborator invalidly invoked on Module {module} with Bundles {module.bundles}"
            raise RuntimeError(msg)

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)

        # Now work through expanding any implicit-ish connections, such as those from port to port.
        # Start by building an adjacency graph of every `PortRef` that's been instantiated

        if module.name == "TestSystem":
            print(5)

        portconns = dict()
        for inst in module.instances.values():
            for port, conn in inst.conns.items():
                if isinstance(conn, PortRef):
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
                if isinstance(portconn, Signal):
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
                sig = lastmod.ports.get(portref.portname, None)
                if sig is not None:  # Clone it, and remove any Port-attributes
                    sig = copy.copy(sig)
                    sig.vis = Visibility.INTERNAL
                    sig.direction = PortDir.NONE
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
                        for path, flat_port in flat_bundle_port.signals.items():
                            # Note `flat_port.name` will be `inst`'s name, i.e. `_mybus_clk_`
                            # Whereas its `path` will line up to `flat`'s namespace, i.e. `['bus']`
                            inst.conns[flat_port.name] = flat.signals[path]
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
            for portname, conn in inst.conns.items():
                if isinstance(conn, AnonymousBundle):
                    raise NotImplementedError
                    # Get the flattened version
                    flat = self.anon_replacements.get(id(conn), None)
                    if flat is None:
                        flat = self.flatten_anonymous_bundle(conn)
                        self.anon_replacements[id(conn)] = flat
                    for flatname, flatsig in flat.signals.items():
                        inst_signame = inst_flat.signals[flatname].name
                        inst.conns[inst_signame] = flatsig
                    # And remove the connection to the original Bundle(s)
                    inst.conns.pop(portname)

                    raise NotImplementedError
                    # inst.conns[portname] = conn_replacements[conn.name][portname]

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
                # or conn.of is not port.of ## FIXME: this is the "exact type equivalence" so heavily debated. Disabled.
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


class ElabPass(Enum):
    """ Enumerated Elaborator Passes
    Each has a `value` attribute which is an Elaborator-pass, 
    and a `name` attribute which is a (Python-enum-style) capitalized name. 
    Specifying  """

    RUN_GENERATORS = GeneratorElaborator
    IMPLICIT_BUNDLES = ImplicitBundles
    BUNDLE_CONN_TYPES = BundleConnTypes
    FLATTEN_BUNDLES = BundleFlattener
    IMPLICIT_SIGNALS = ImplicitSignals
    SIGNAL_CONN_TYPES = SignalConnTypes

    @classmethod
    def default(cls) -> List["ElabPass"]:
        """ Return the default ordered Elaborator Passes. """
        # Returns each in definition order
        return list(ElabPass)


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
