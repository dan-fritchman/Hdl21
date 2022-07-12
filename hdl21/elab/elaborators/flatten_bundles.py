"""
# Bundle-Flattening Elaborator Pass 
"""

# Std-Lib Imports
import copy
from typing import Dict, List, Tuple, Union

# PyPi
from pydantic.dataclasses import dataclass

# Local imports
from ...module import Module
from ...instance import Instance
from ...bundle import (
    AnonymousBundle,
    Bundle,
    BundleInstance,
    BundleRef,
)
from ...signal import PortDir, Signal, Visibility

# Import the base class
from .base import Elaborator


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


class BundleScope:
    """ Scope-worth of Signals for a flattened Bundle """

    path: Path
    pathstr: PathStr
    signals: Dict[PathStr, List[Signal]]


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


class BundleFlattener(Elaborator):
    """ Bundle-Flattening Elaborator Pass """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Class-specific data tracking.
        # There's *plenty* to be done here, as this class largely maps "folded" Signals into "flattened" ones.

        # Bundle (definition) replacements, id(Bundle) => FlatBundle
        self.bundle_defs: Dict[int, FlatBundleDef] = dict()
        # BundleInstance replacements, id(BundleInst) => FlatBundleInst
        self.bundle_insts: Dict[int, FlatBundleInst] = dict()
        # AnonymousBundle replacements, id(AnonBundle) => Tbd
        self.anon_bundles: Dict[int, "Tbd"] = dict()
        # Replacement-values by Module and attribute-name. (id(Module), attrname) => FlatBundleInst
        self.module_attrs: Dict[Tuple[int, str], FlatBundleInst] = dict()

    def elaborate_module(self, module: Module) -> Module:
        """ Flatten Module `module`s Bundles, replacing them with newly-created Signals.
        Reconnect the flattened Signals to any Instances connected to said Bundles. """

        # Remove and replace each `BundleInstance` from the Module
        while module.bundles:
            name, bundle_inst = module.bundles.popitem()
            module.namespace.pop(name)
            self.replace_bundle_inst(module, bundle_inst)
        
        # Go through each Instance, replacing `AnonymousBundle`s with their referents
        # Note `Module`s do not store `AnonymousBundle`s directly, so we don't have a quicker way 
        # to find them all than traversing the connections to each instance and array. 
        for inst in instances_and_arrays(module):
            anon_conns = {portname: conn for portname, conn in inst.conns.items() if isinstance(conn, AnonymousBundle)}
            for portname, anon_bundle in anon_conns.items():
                self.replace_anon_bundle_conn(inst=inst, portname=portname, anon=anon_bundle)

        return module
    
    def replace_bundle_inst(self, module: Module, bundle_inst: BundleInstance):
        """ Replace a `BundleInstance`, flattening its Signals into `module`'s namespace, 
        and replacing all of its Instance connections with their flattened replacements. """

        # Check we haven't (somehow) already flattened it
        if id(bundle_inst) in self.bundle_insts:
            msg = f"Bundle Instance {bundle_inst} in Module {module} flattened more than once. Was it actually part of another Module?"
            self.fail(msg)

        # Flatten it and store the result in our caches
        flat = self.flatten_bundle_inst(bundle_inst)
        self.bundle_insts[id(bundle_inst)] = flat
        self.module_attrs[(id(module), bundle_inst.name)] = flat

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
        for portref in list(bundle_inst.connected_ports):
            self.replace_bundle_conn(inst=portref.inst, portname=portref.portname, flat=flat)

        # Re-connect any BundleRefs that `bundle` has given out, as in the form:
        # i = SomeBundle()       # Theoretical Bundle with signal-attribute `s`
        # x = SomeModule(s=i.s)  # Connects `BundleRef` `i.s`
        # FIXME: this needs to happen for hierarchical bundles too
        for bref in bundle_inst.refs_to_me.values():
            # Resolve to the flattened signal
            flatsig = self.resolve_bundleref(bref)

            # Walk through connected Instances, replacing any connections to this `BundleRef` with `flatsig`
            for portref in list(bref.connected_ports):
                portref.inst.replace(portref.portname, flatsig)

    def replace_anon_bundle_conn(self, inst: Instance, portname: str, anon: AnonymousBundle):
        """ Replace an `AnonymousBundle` connection with its (already) flattened referents. """

        flat_bundle_port = self.module_attrs.get((id(inst._resolved), portname), None)
        if flat_bundle_port is None:
            msg = f"Invalid Port Connection to {portname} on Instance {inst}"
            self.fail(msg)

        # Replace the connection to each flattened Signal
        for pathstr, flat_port in flat_bundle_port.signals.items():
            # Note `flat_port.name` will be `inst`'s name, i.e. `_mybus_clk_`
            # Whereas its `path` will line up to `flat`'s namespace, i.e. `['bus']`
            attr = anon.get(pathstr.val)
            if attr is None:
                msg = f"Connection {pathstr.val} missing from AnonymousBundle connected to Port {portname} on Instance {inst}"
                self.fail(msg)

            if isinstance(attr, BundleRef): # Resolve any references
                attr = self.resolve_bundleref(attr)
            elif isinstance(attr, Signal):
                ...  # Nothing to do, carry along with the Module-owned `Signal` attribute
            else:
                raise TypeError(f"Invalid AnonymousBundle attribute {attr}")

            inst.connect(flat_port.name, attr)
        
        # And now we can remove the `AnonymousBundle` connection 
        inst.disconnect(portname)


    def replace_bundle_conn(self, inst: Instance, portname: str, flat: FlatBundleInst):
        """ Replace a connection to a `BundleInstance` with a connections to the Signals of a `FlatBundleInst` """

        flat_bundle_port = self.module_attrs.get((id(inst._resolved), portname), None)
        if flat_bundle_port is None:
            msg = f"Invalid Port Connection to {portname} on Instance {inst}"
            self.fail(msg)

        # Disconnect the old hierarchical Bundle port
        inst.disconnect(portname)

        # Replace the connection to each flattened Signal
        for pathstr, flat_port in flat_bundle_port.signals.items():
            # Note `flat_port.name` will be `inst`'s name, i.e. `_mybus_clk_`
            # Whereas its `path` will line up to `flat`'s namespace, i.e. `['bus']`
            inst.connect(flat_port.name, flat.signals[pathstr])

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
                    msg = f"Error Flattening {bundle}: colliding flattened Signal names for {sig} and {flat.signals[pathstr]}"
                    self.fail(msg)
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

    def flatten_anonymous_bundle(self, anon: AnonymousBundle) -> FlatBundleInst:
        """ Flatten an `AnonymousBundle`. 
        Differs from bundle-class instances in that each attribute of anonymous-bundles 
        are generally "references", owned by something else, commonly a Module. """

        raise NotImplementedError

        if id(anon) in self.anon_bundles:
            return self.anon_bundles[id(anon)]

        # All scalar Signals are owned by the Module, and can be used in the flat bundle as-is.
        # Note this copies the `signals` *dictionary* without copying the Signals themselves.
        signals = copy.copy(anon.signals)

        for name, bundleref in anon.refs_to_others.items():
            msg = f"Unsupported: Bundle-valued Ref to {bundleref} in {anon}"
            self.fail(msg)
            resolved = self.resolve_bundleref(bundleref)
            if isinstance(resolved, Signal):
                signals[name] = resolved
            elif isinstance(resolved, BundleInstance):
                raise NotImplementedError  # Yeah thats the hard part

        # Cache and return ther new `FlatBundleInst`
        flat = FlatBundleInst(src=anon, signals=signals)
        self.anon_bundles[id(anon)] = flat
        return flat


    def resolve_bundleref(self, bref: BundleRef) -> Union[Signal, FlatBundleInst]:
        """ Resolve a bundle-reference to a Signal or Flattened Bundle thereof. 
        NOTE: currently only the scalar Signal resolution case is supported; nested Bundles are TBC. """

        if isinstance(bref.parent, BundleInstance):
            # Get the flattened version of the parent 
            flat_parent = self.bundle_insts.get(id(bref.parent), None)
            if flat_parent is None:
                msg = f"Invalid BundleRef to {bref.parent}"
                self.fail(msg)
            
            # And look up the Signal in the flattened version
            flatsig = flat_parent.signals.get(PathStr(bref.attrname), None)
            if flatsig is None:
                msg = f"Port {bref.attrname} not found in Bundle {bref.parent.of.name}"
                self.fail(msg)
            if not isinstance(flatsig, Signal):
                msg = f"Unsupported: BundleRef to non-Signal {flatsig}"
                raise TypeError(msg)
            
            # Success! Return the Signal
            return flatsig

        if isinstance(bref.parent, BundleRef):
            raise NotImplementedError # Nested bundle refs, TBC

        raise TypeError(f"BundleRef parent for {bref}")

def instances_and_arrays(module: Module) -> List[Instance]:
    """ Get a list of `module`'s instances and instance arrays. """
    return list(module.instances.values()) + list(module.instarrays.values())
