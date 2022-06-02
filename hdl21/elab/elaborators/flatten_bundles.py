"""
# Bundle-Flattening Elaborator Pass 
"""

# Std-Lib Imports
import copy
from typing import Dict, List, Tuple

# PyPi
from pydantic.dataclasses import dataclass

# Local imports
from ...module import Module
from ...bundle import AnonymousBundle, Bundle, BundleInstance, resolve_bundle_ref
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

            # Re-connect any BundleRefs that `bundle` has given out, as in the form:
            # i = SomeBundle()       # Theoretical Bundle with signal-attribute `s`
            # x = SomeModule(s=i.s)  # Connects `BundleRef` `i.s`
            # FIXME: this needs to happen for hierarchical bundles too
            for bref in bundle_inst.refs.values():
                resolved_bref = resolve_bundle_ref(bref)
                if isinstance(resolved_bref, BundleInstance):
                    msg = f"Bundle Reference to {resolved_bref} in {bref}"
                    raise NotImplementedError(msg)

                elif isinstance(resolved_bref, Signal):
                    # FIXME: this may need to traverse some hierarchy...
                    flatsig = flat.signals.get(PathStr(bref.attrname), None)
                    if flatsig is None:
                        msg = f"Port {bref.attrname} not found in Bundle {bundle_inst.of.name}"
                        raise RuntimeError(msg)
                else:
                    raise TypeError(f"Resolved BundleRef {bref} to {resolved_bref}")

                # Walk through our Instances, replacing any connections to this `BundleRef` with `flatsig`
                # FIXME: a better word for "instances or arrays thereof"; we already used "connectable"
                connectables = list(module.instances.values()) + list(
                    module.instarrays.values()
                )
                for inst in connectables:
                    for attrname, conn in inst.conns.items():
                        if conn is bref:
                            inst.conns[attrname] = flatsig

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
                    msg = f"Error Flattening {bundle}: colliding flattened Signal names for {sig} and {flat.signals[pathstr]}"
                    raise RuntimeError(msg)
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

        raise NotImplementedError(f"Nested AnonymousBundle")

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
