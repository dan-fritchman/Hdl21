"""
# Bundle-Flattening Elaborator Pass 
"""

# Std-Lib Imports
import copy
from typing import Dict, List, Tuple, Union, Optional

# PyPi
from pydantic.dataclasses import dataclass

# Local imports
from ...module import Module
from ...instance import Instance
from ... import Slice, Concat, NoConn, PortRef
from ...bundle import (
    AnonymousBundle,
    Bundle,
    BundleInstance,
    BundleRef,
)
from ...signal import PortDir, Signal, Visibility
from .resolve_ref_types import update_ref_deps

# Import the base class
from .base import Elaborator


@dataclass
class Path:
    """Hierarchical String-Valued Path"""

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
    """Single-String Representation of `Path`"""

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
class BundleScope:
    """Scope-worth of Signals for a flattened Bundle"""

    path: Path
    pathstr: PathStr
    # Flattened signals-dict, keyed by Path
    # Includes *all* Signals in *all* sub-scopes.
    signals: Dict[PathStr, Signal]
    # Hierarchical scopes
    # All Signals inside sub-scopes are references to elements in `signals`.
    scopes: Dict[PathStr, "BundleScope"]

    @classmethod
    def root(
        cls, signals: Optional[dict] = None, scopes: Optional[dict] = None
    ) -> "BundleScope":
        """Create a new root scope"""
        signals = signals or {}
        scopes = scopes or {}
        return cls(
            path=Path([]),
            pathstr=PathStr(""),
            signals=signals,
            scopes=scopes,
        )

    def add_subscope(self, name: str, scope: "BundleScope"):
        """Add a sub `BundleScope`. Also add its signals to our parent dict."""
        self.scopes[PathStr(name)] = scope
        for k, v in scope.signals.items():
            self.signals[PathStr.concat(name, k)] = v


BundleScope.__pydantic_model__.update_forward_refs()


@dataclass
class FlatBundleDef:
    """Flattened Bundle Definition"""

    # Source/ Original Bundle
    src: Bundle
    # Flattened signals-dict, keyed by Path
    # Includes *all* Signals in *all* sub-scopes.
    signals: Dict[PathStr, Signal]
    # Hierarchical scopes of flattened internal Bundles
    scopes: Dict[PathStr, BundleScope]


@dataclass
class FlatBundleInst:
    """Flattened Bundle Instance"""

    # Source/ Original Bundle
    src: BundleInstance
    # Root `BundleScope`
    root_scope: BundleScope

    @property
    def signals(self):
        return self.root_scope.signals


class BundleFlattener(Elaborator):
    """Bundle-Flattening Elaborator Pass"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Class-specific data tracking.
        # There's *plenty* to be done here, as this class largely maps "folded" Signals into "flattened" ones.

        # Bundle (definition) replacements, id(Bundle) => FlatBundle
        self.bundle_defs: Dict[int, FlatBundleDef] = dict()
        # BundleInstance replacements, id(BundleInst) => FlatBundleInst
        self.bundle_insts: Dict[int, FlatBundleInst] = dict()
        # Replacement flattened Bundle-valued ports.
        # Keyed by Module and attribute-name.
        # (id(Module), attrname) => FlatBundleInst
        self.flat_bundle_ports: Dict[Tuple[int, str], FlatBundleInst] = dict()
        # AnonymousBundle replacements, id(AnonBundle) => BundleScope
        self.anon_bundles: Dict[int, BundleScope] = dict()

    def elaborate_module(self, module: Module) -> Module:
        """Flatten Module `module`s Bundles, replacing them with newly-created Signals.
        Reconnect the flattened Signals to any Instances connected to said Bundles."""

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
        if id(bundle_inst) in self.bundle_insts:
            msg = f"Bundle Instance {bundle_inst} in Module {module} flattened more than once. Was it actually part of another Module?"
            self.fail(msg)

        # Flatten it
        flat = self.flatten_bundle_inst(bundle_inst)

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

        # Store the result in our caches
        self.bundle_insts[id(bundle_inst)] = flat
        if bundle_inst.port:
            self.flat_bundle_ports[(id(module), bundle_inst.name)] = flat

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
        Replace a connection to a `BundleInstance` with a connections to the Signals of a `FlatBundleInst`.
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
        which are stored in a `FlatBundleInst` keyed by `x`, `y`, and `z`.
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

        flat_bundle_port = self.flat_bundle_ports.get(
            (id(inst._resolved), portname), None
        )
        if flat_bundle_port is None:
            msg = f"Invalid Port Connection to {portname} on Instance {inst}"
            self.fail(msg)

        # Disconnect the old hierarchical Bundle port
        inst.disconnect(portname)

        # Replace the connection to each flattened Signal
        for pathstr, flat_port in flat_bundle_port.signals.items():
            # Note in analogy to the commentary above -
            # * `pathstr` will be relative to the Bundle definition
            #   * In the example, its values will be `x`, `y`, and `z`.
            # * `flat_port.name` will be the instance's new port names
            #   * In the example, its values will be `inner_b_x`, `inner_b_y`, and `inner_b_z`.
            # * Neither takes on the values `outer_b_x`, `outer_b_y`, and `outer_b_z`.
            #   * These would be `flat.signals[pathstr].name`
            if pathstr not in flat.signals:
                msg = f"Missing connection to `{pathstr.val}` "
                msg += f"in Connection to `{portname}` on Instance `{inst.name}`. "
                msg += f"Has Signals `{[p.val for p in flat.signals.keys()]}`, "
                msg += f"but no `{pathstr.val}`."
                self.fail(msg)
            inst.connect(flat_port.name, flat.signals[pathstr])

    def flatten_bundle_def(self, bundle: Bundle) -> FlatBundleDef:
        """
        Flatten a `Bundle` (definition).
        Note Signals *are not* copied upon `FlatBundleDef` creation,
        but must be while unrolling to each `FlatBundleInst`.
        """

        if id(bundle) in self.bundle_defs:
            return self.bundle_defs[id(bundle)]  # Already done!

        # Create the flattened version, initializing it with `bundle`s scalar Signals,
        # Converting their keys to `Path` elements
        flat = FlatBundleDef(
            src=bundle,
            signals={
                PathStr.from_list([sig.name]): sig for sig in bundle.signals.values()
            },
            scopes={},
        )
        # Depth-first walk any bundle-instance's definitions, flattening them
        for instname, i in bundle.bundles.items():

            # Create a new scope for the bundle-instance
            scope_path = Path([instname])
            scope_pathstr = PathStr.from_path(scope_path)
            scope = flat.scopes[instname] = BundleScope(
                path=scope_path,
                pathstr=scope_pathstr,
                signals={},
                scopes={},
            )

            # Recursively flatten the bundle-instance's definition
            iflat = self.flatten_bundle_def(i.of)

            scope.scopes = copy.copy(iflat.scopes)

            # And add its contents to our flattened definition
            for path_suffix, sig in iflat.signals.items():
                # Add the Signal to the new scope
                if path_suffix in scope.signals:
                    msg = f"Error Flattening {bundle}: colliding flattened Signal names for {sig} and {scope.signals[path_suffix]}"
                    self.fail(msg)
                scope.signals[path_suffix] = sig

                # And add them all to the root `signals` dict, with a prepended path
                root_pathstr = PathStr.concat(i.name, path_suffix)
                if root_pathstr in flat.signals:
                    msg = f"Error Flattening {bundle}: colliding flattened Signal names for {sig} and {flat.signals[root_pathstr]}"
                    self.fail(msg)
                flat.signals[root_pathstr] = sig

        # Store it in our cache, and return
        self.bundle_defs[id(bundle)] = flat
        return flat

    def flatten_bundle_inst(self, bundle_inst: BundleInstance) -> FlatBundleInst:
        """Convert nested Bundle `bundle` into a flattened `FlatBundleInst` of scalar Signals.
        Signals are copied in the creation of each `BundleInstance`, so no further copying is required at the Module-level."""

        # Get the (flattened) Bundle-definition
        flatdef = self.flatten_bundle_def(bundle_inst.of)

        # Copy and rename its signals
        signals: Dict[str, Signal] = dict()
        replacement_signals: Dict[int, Signal] = dict()
        for pathstr, oldsig in flatdef.signals.items():
            sig = replacement_signals[id(oldsig)] = copy.deepcopy(oldsig)
            sig.name = pathstr.to_name()
            signals[pathstr] = sig

        # Copy its sub-Bundle `Scope`s
        scopes = {
            PathStr(name): self.copy_bundle_scope(scope, replacement_signals)
            for name, scope in flatdef.scopes.items()
        }

        # And return a new `FlatBundleInst`
        scope = BundleScope.root(signals=signals, scopes=scopes)
        return FlatBundleInst(src=bundle_inst, root_scope=scope)

    def copy_bundle_scope(
        self, scope: BundleScope, signal_replacements: Dict[int, Signal]
    ) -> BundleScope:
        """Recursively copy a `BundleScope`, replacing its `signals` with those in `signal_replacements`."""
        signals = {
            name: signal_replacements[id(sig)] for name, sig in scope.signals.items()
        }
        scopes = {
            PathStr(name): self.copy_bundle_scope(scope, signal_replacements)
            for name, scope in scope.scopes.items()
        }
        return BundleScope(
            path=scope.path, pathstr=scope.pathstr, signals=signals, scopes=scopes
        )

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

        if id(anon) in self.anon_bundles:
            return self.anon_bundles[id(anon)]

        scope = BundleScope.root()

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
                scope.signals[PathStr(name)] = attr

            # Finally handle nested, Bundle-like types, which produce sub-scopes
            elif isinstance(attr, BundleInstance):
                # BundleInstances have all been visited by now, and hence better be in the cache
                flat_inst = self.bundle_insts.get(id(attr), None)
                if flat_inst is None:
                    self.fail(f"Invalid AnonymousBundle attribute {attr}")
                scope.add_subscope(name, flat_inst.root_scope)

            elif isinstance(attr, AnonymousBundle):
                subscope = self.flatten_anonymous_bundle(attr)
                scope.add_subscope(name, subscope)

            elif isinstance(attr, BundleScope):
                scope.add_subscope(name, attr)
            else:
                raise TypeError  # Shouldn't be reachable

        self.anon_bundles[id(anon)] = scope
        return scope

    def resolve_bundleref(self, bref: BundleRef) -> Union[Signal, BundleScope]:
        """Resolve a bundle-reference to a Signal or Flattened Bundle thereof."""

        if bref.resolved is not None:
            return bref.resolved  # Already done

        # Get its path and root BundleInstance
        path: List[str] = bref.path()
        root: BundleInstance = bref.root()

        # Get the flattened version of the root BundleInstance
        flat_root = self.bundle_insts.get(id(root), None)
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
        self, flat: Union[FlatBundleDef, FlatBundleInst], path: Path
    ) -> Union[Signal, BundleScope]:
        """Resolve `path` in the flattend bundle `flat`, producing either a Signal or nested BundleScope."""
        if isinstance(flat, FlatBundleDef):
            ns = flat
        elif isinstance(flat, FlatBundleInst):
            ns = flat.root_scope
        else:
            msg = f"Invalid target for path resolution {flat} must be FlatBundleDef or FlatBundleInst"
            return self.fail(msg)

        for seg in path.segs:
            seg = PathStr(seg)
            if seg in ns.signals:
                ns = ns.signals[seg]
            elif seg in ns.scopes:
                ns = ns.scopes[seg]
            else:
                pathstr = ".".join(path.segs)
                msg = f"Cannot resolve path `{pathstr}` in `{flat.src.name}`"
                return self.fail(msg)
        return ns


def instances_and_arrays(module: Module) -> List[Instance]:
    """Get a list of `module`'s instances and instance arrays."""
    return list(module.instances.values()) + list(module.instarrays.values())
