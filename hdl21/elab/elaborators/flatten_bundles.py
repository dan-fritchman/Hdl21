"""
# Bundle-Flattening Elaborator Pass 
"""

# Std-Lib Imports
import copy
from dataclasses import field
from typing import Dict, List, Union, Optional

# PyPi
from pydantic.dataclasses import dataclass

# Local imports
from ...module import Module
from ...instance import Instance
from ... import Slice, Concat, NoConn, PortRef
from ...bundle import (
    AnonymousBundle,
    BundleInstance,
    BundleRef,
)
from ...signal import PortDir, Signal, Visibility
from ...instantiable import io
from .resolve_ref_types import update_ref_deps

# Import the base class
from .base import Elaborator


@dataclass(frozen=True)
class Path:
    """
    # Hierarchical String-Valued Path

    This contains a list which is mutable, but... don't mutate it.
    The `Path` object itself is designed to be hashed,
    particularly for by-key lookups of hierarchical Bundle attributes.
    Don't ever mutate them; create new ones.
    """

    segs: List[str]  # List of path segments

    def append(self, suffix: "Path") -> "Path":
        """Append `suffix`. Returns a *new* Path."""
        return Path(segs=self.segs + suffix.segs)

    def prepend(self, prefix: "Path") -> "Path":
        """Prepend `prefix`. Returns a *new* Path."""
        return Path(segs=prefix.segs + self.segs)

    def to_name(self) -> str:
        return "_".join(self.segs)

    def __hash__(self):
        return hash(tuple(self.segs))

    def __eq__(self, other: "Path") -> bool:
        if not isinstance(other, Path):
            return NotImplemented
        return self.segs == other.segs


@dataclass
class BundleScope:
    """Scope-worth of Signals for a flattened Bundle"""

    src: Union[BundleInstance, AnonymousBundle]  # Source/ Original Bundle
    parent: Optional["BundleScope"] = None  # Parent Scope

    signals: Dict[Path, Signal] = field(default_factory=dict)
    # Flattened signals-dict, keyed by Path string.
    # Includes *all* Signals in *all* sub-scopes.

    scopes: Dict[Path, "BundleScope"] = field(default_factory=dict)
    # Hierarchical scopes
    # All Signals inside sub-scopes are references to elements in `signals`,
    # at the `path` as they'd be referred to in that Scope.

    def add_subscope(self, name: str, scope: "BundleScope"):
        """Add a sub `BundleScope`. Also add its signals to our parent dict."""

        name = Path([name])
        self.scopes[name] = scope
        scope.parent = self

        for path_suffix, sig in scope.signals.items():
            # And add them all to the root `signals` dict, with a prepended path
            path_from_self = path_suffix.prepend(name)
            if path_from_self in self.signals:
                msg = f"Error Flattening Bundles: colliding flattened Signal names for {sig} and {self.signals[path_from_self]}"
                raise RuntimeError(msg)
            self.signals[path_from_self] = sig


BundleScope.__pydantic_model__.update_forward_refs()


@dataclass
class BundlePortEntry:
    """# Bundle-Port Entry in the Cache
    Hashable combination of a Module and a portname."""

    module: Module
    portname: str

    def __eq__(self, other: "BundlePortEntry") -> bool:
        if not isinstance(other, BundlePortEntry):
            return NotImplemented
        return self.module is other.module and self.portname == other.portname

    def __hash__(self) -> int:
        return hash((id(self.module), self.portname))


@dataclass
class Cache:
    """
    The Bundle Flattening Cache
    Designed to operate at Module level, across multiple Elaborators.
    """

    bundle_insts: Dict[int, BundleScope] = field(default_factory=dict)
    # BundleInstance replacements, {id(BundleInst) => BundleScope}

    anon_bundles: Dict[int, BundleScope] = field(default_factory=dict)
    # AnonymousBundle replacements, {id(AnonBundle) => BundleScope}

    flat_bundle_ports: Dict[BundlePortEntry, BundleScope] = field(default_factory=dict)
    # Replacement flattened Bundle-valued ports.
    # Keyed by Module and port-name.
    # {BundlePortEntry(module, portname) => BundleScope}


# The module-scope flattening cache
THE_CACHE = Cache()


class BundleFlattener(Elaborator):
    """Bundle-Flattening Elaborator Pass"""

    def elaborate_module(self, module: Module) -> Module:
        """Flatten Module `module`s Bundles, replacing them with newly-created Signals.
        Reconnect the flattened Signals to any Instances connected to said Bundles."""

        # Cache the state of the Module's IOs before flattening
        module._pre_flattening_io = copy.copy(io(module))

        # Remove and replace each `BundleInstance` from the Module
        while module.bundles:
            name, bundle_inst = module.bundles.popitem()
            module.namespace.pop(name)
            self.replace_bundle_inst(module, bundle_inst)

        # Go through each Instance, replacing `AnonymousBundle`s with their referents
        # Note `Module`s do not store `AnonymousBundle`s directly, so we don't have a quicker way
        # to find them all than traversing the connections to each instance and array.
        for inst in instances_and_arrays(module):
            anon_conns = {
                portname: conn
                for portname, conn in inst.conns.items()
                if isinstance(conn, AnonymousBundle)
            }
            for portname, anon_bundle in anon_conns.items():
                self.replace_anon_bundle_conn(
                    inst=inst, portname=portname, anon=anon_bundle
                )

        return module

    def replace_bundle_inst(self, module: Module, bundle_inst: BundleInstance):
        """Replace a `BundleInstance`, flattening its Signals into `module`'s namespace,
        and replacing all of its Instance connections with their flattened replacements."""

        # Check we haven't (somehow) already replaced it
        if id(bundle_inst) in THE_CACHE.bundle_insts:
            msg = f"Bundle Instance {bundle_inst} in Module {module} flattened more than once. Was it actually part of another Module?"
            self.fail(msg)

        # Flatten it
        flat = self.flatten_bundle_inst(bundle_inst, path=Path([]))

        # Add each flattened Signal. Note flattened Signals are modified in-place.
        for pathstr, sig in flat.signals.items():
            # Rename the signal, prepending the bundle-instance's name
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

        # Store the result in our caches
        THE_CACHE.bundle_insts[id(bundle_inst)] = flat
        if bundle_inst.port:
            entry = BundlePortEntry(module, bundle_inst.name)
            THE_CACHE.flat_bundle_ports[entry] = flat

        # Replace connections to any connected instances
        for portref in list(bundle_inst._connected_ports):
            self.replace_bundle_conn(
                inst=portref.inst, portname=portref.portname, flat=flat
            )

        # Kick off recursive `Ref` replacement for any (potential nested)
        # references `bundle_inst` has given out.
        self.resolve_bundlerefs(bundle_inst)

    def resolve_bundlerefs(self, hasrefs: Union[BundleInstance, BundleRef]) -> None:
        """Resolve all BundleRefs that `hasrefs` has given out."""
        for bref in hasrefs.refs_to_me.values():
            # Recursively get references it has handed out
            self.resolve_bundlerefs(bref)
            # And resolve `bref` itself
            self.resolve_bundleref(bref)

    def replace_bundle_conn(self, inst: Instance, portname: str, flat: BundleScope):
        """
        Replace a connection to a `BundleInstance` with a connections to the Signals of a `BundleScope`.
        At this point, if we started with a circuit like:

        ```python
        @h.bundle
        class B:
            x, y, z = h.Signals(3)

        @h.module
        class Inner:
            inner_b = B(port=True)

        @h.module
        class Outer:
            outer_b = B()
            inner = Inner(b=outer_b)
        ```
        At the point of getting here to reconnect the port `inner.b`,
        the `Inner` module has been flattened, and looks more like

        ```
        @h.module
        class Inner:
            inner_b_x, inner_b_y, inner_b_z = h.Ports(3)
        ```

        The bundle instances in `Outer` have also been flattened.
        It now has signals named `outer_b_x`, `outer_b_y`, and `outer_b_z`,
        which are stored in a `BundleScope` keyed by `x`, `y`, and `z`.
        After this function it will (or should) look like:

        ```
        @h.module
        class Outer:
            outer_b_z, outer_b_y, outer_b_z  = h.Signals(3)
            inner = Inner(inner_b_x=outer_b_x, inner_b_y=outer_b_y, inner_b_z=outer_b_z)
        ```

        The primary mental gymnastics here are in naming,
        particularly between the Instance and instantiating module.
        """

        entry = BundlePortEntry(inst._resolved, portname)
        flat_bundle_port = THE_CACHE.flat_bundle_ports.get(entry, None)
        if flat_bundle_port is None:
            msg = f"Invalid Port Connection to {portname} on Instance {inst}"
            self.fail(msg)

        # Disconnect the old hierarchical Bundle port
        inst.disconnect(portname)

        # Replace the connection to each flattened Signal
        for path, flat_port in flat_bundle_port.signals.items():
            # Note in analogy to the commentary above -
            # * `path` will be relative to the Bundle definition
            #   * In the example, its values will be `x`, `y`, and `z`.
            # * `flat_port.name` will be the instance's new port names
            #   * In the example, its values will be `inner_b_x`, `inner_b_y`, and `inner_b_z`.
            # * Neither takes on the values `outer_b_x`, `outer_b_y`, and `outer_b_z`.
            #   * These would be `flat.signals[path].name`
            if path not in flat.signals:
                msg = f"Missing connection to `{path}` "
                msg += f"in Connection to `{portname}` on Instance `{inst.name}`. "
                msg += f"Has Signals `{list(flat.signals.keys())}`, "
                msg += f"but no `{path}`."
                self.fail(msg)
            inst.connect(flat_port.name, flat.signals[path])

    def flatten_bundle_inst(
        self, bundle_inst: BundleInstance, path: Path
    ) -> BundleScope:

        bundle_def = bundle_inst.of
        scope = BundleScope(src=bundle_inst)

        # Copy each scalar signal, retaining its original name as the key in `scope.signals`
        for sig in bundle_def.signals.values():
            signal_path = Path([sig.name])
            if signal_path in scope.signals:
                self.fail(f"Doubly defined Signal {sig} in {bundle_inst}")
            newsig = copy.deepcopy(sig)
            newsig.name = signal_path.to_name()
            scope.signals[signal_path] = newsig

        # And recursively do this to all sub-bundle instances, adding them to `scopes` along the way.
        for sub_bundle_inst in bundle_def.bundles.values():
            subpath = path.append(Path([sub_bundle_inst.name]))
            subscope = self.flatten_bundle_inst(sub_bundle_inst, subpath)
            scope.add_subscope(name=sub_bundle_inst.name, scope=subscope)

        return scope

    def replace_anon_bundle_conn(
        self, inst: Instance, portname: str, anon: AnonymousBundle
    ):
        """Replace an `AnonymousBundle` connection with its (already) flattened referents."""

        anon_scope: BundleScope = self.flatten_anonymous_bundle(anon)
        self.replace_bundle_conn(inst, portname, anon_scope)

    def flatten_anonymous_bundle(self, anon: AnonymousBundle) -> BundleScope:
        """Flatten an `AnonymousBundle`.
        Differs from bundle-class instances in that each attribute of anonymous-bundles
        are generally "references", owned by something else, commonly a Module."""

        if id(anon) in THE_CACHE.anon_bundles:
            return THE_CACHE.anon_bundles[id(anon)]

        scope = BundleScope(src=anon)

        for name, attr in anon._namespace.items():
            # First resolve any references
            # Note at this point in elaboration, these Anon-Bundles are the sole remaining place `PortRef`s can hide.
            # They are also the last place where `BundleRef`s will be resolved,
            # although the others just have been, earlier in this elaborator pass.
            if isinstance(attr, (BundleRef, PortRef)):
                attr = self.resolve_bundleref(attr)

            if isinstance(attr, NoConn):  # Invalid
                self.fail(f"Invalid AnonymousBundle NoConn attribute {attr} in {anon}")

            elif isinstance(attr, (Signal, Slice, Concat)):
                # "Scalar" signals get added to the result scope
                scope.signals[Path([name])] = attr

            # Finally handle nested, Bundle-like types, which produce sub-scopes
            elif isinstance(attr, BundleInstance):
                # BundleInstances have all been visited by now, and hence better be in the cache
                flat_inst = THE_CACHE.bundle_insts.get(id(attr), None)
                if flat_inst is None:
                    self.fail(f"Invalid AnonymousBundle attribute {attr}")
                scope.add_subscope(name, flat_inst)

            elif isinstance(attr, AnonymousBundle):
                subscope = self.flatten_anonymous_bundle(attr)
                scope.add_subscope(name, subscope)

            elif isinstance(attr, BundleScope):
                scope.add_subscope(name, attr)
            else:  # Shouldn't be reachable
                raise TypeError(f"Invalid AnonBundle attribute {attr}")

        THE_CACHE.anon_bundles[id(anon)] = scope
        return scope

    def resolve_bundleref(self, bref: BundleRef) -> Union[Signal, BundleScope]:
        """Resolve a bundle-reference to a Signal or Flattened Bundle thereof."""

        if bref.resolved is not None:
            return bref.resolved  # Already done

        # Get its path and root BundleInstance
        path: List[str] = bref.path()
        root: BundleInstance = bref.root()

        # Get the flattened version of the root BundleInstance
        flat_root = THE_CACHE.bundle_insts.get(id(root), None)
        if flat_root is None:
            msg = f"Invalid BundleRef to {bref.parent}"
            self.fail(msg)

        bref.resolved = resolved = self.resolve_path(flat_root, Path(path))

        if isinstance(resolved, BundleScope):
            for connected_port in list(bref._connected_ports):
                self.replace_bundle_conn(
                    inst=connected_port.inst,
                    portname=connected_port.portname,
                    flat=resolved,
                )
            return resolved

        if isinstance(resolved, Signal):
            update_ref_deps(bref, resolved)
            return resolved

        return self.fail(f"BundleRef {bref} resolved to invalid {resolved}")

    def resolve_path(
        self, scope: BundleScope, path: Path
    ) -> Union[Signal, BundleScope]:
        """Resolve `path` in the flattend `scope`, producing either a Signal or nested BundleScope."""

        ns = scope
        for seg in path.segs:
            seg = Path([seg])
            if seg in ns.signals:
                ns = ns.signals[seg]
            elif seg in ns.scopes:
                ns = ns.scopes[seg]
            else:
                pathstr = ".".join(path.segs)
                if isinstance(scope.src, BundleInstance):
                    msg = f"Cannot resolve path `{pathstr}` in `{scope.src.name}`"
                else:
                    msg = f"Cannot resolve path `{pathstr}` in `{scope}`"
                return self.fail(msg)
        return ns


def instances_and_arrays(module: Module) -> List[Instance]:
    """Get a list of `module`'s instances and instance arrays."""
    return list(module.instances.values()) + list(module.instarrays.values())


__all__ = ["BundleFlattener"]
