"""
# Helper for resolving the "types" of references. 

Note "types" here does not mean Python-types, but something more like "connection types". 
Resolving a reference "type" produces either a Signal or BundleInstance, 
which is "compatible with", but not equal to, the ultimate referent. 

For example: 

```python
@h.module
class Inner:
    p = h.Port()

@h.module
class Outer:
    i = Inner() 

# Create a `PortRef`
ref = Outer.i.p

# All of these succeed:
assert ref is Outer.i.p
assert resolve_portref_type(ref) is not Outer.i.p
assert resolve_portref_type(ref) is not Inner.p
```

Here `ref` will ultimately refer to the a Signal within an `Instance` of `Inner`. 
At the time of calling `resolve_portref_type`, no such Signal exists. 
The result of `resolve_portref_type` is therefore the `Inner` *Module definition level* Signal object. 
This is often required e.g. for connection-validity checking, or for copying to new Signals.

The important thing is: don't take the results of `resolve_*_type` as the actual referents! 
"""

# Std-Lib Imports
from typing import Union, Callable

# Local imports
from ...portref import PortRef
from ...connect import Connectable
from ...signal import Signal
from ...bundle import (
    BundleInstance,
    BundleRef,
)


def fail(msg: str) -> None:
    # The default failure handler
    raise RuntimeError(msg)


def resolve_bundleref_type(
    bref: BundleRef, failer: Callable = fail
) -> Union[Signal, BundleInstance]:
    """
    Resolve a bundle-reference to either a `Signal` or sub-`Bundle` Instance.

    NOTE this returns a *representative* signal or bundle instance,
    i.e. one with the correct type and width - not *the signal* for a given instance.
    In other words: this is fine for connection-validity checking,
    but *not* for copying signals during flattening.
    Hence the "type" name suffix, although what we return is not really a type.
    """

    if isinstance(bref.parent, BundleInstance):  # Parent is a BundleInstance.
        parent = bref.parent
    elif isinstance(
        bref.parent, BundleRef
    ):  # Nested reference. Recursively resolve the parent.
        parent = resolve_bundleref_type(bref.parent, failer)
    else:
        failer(f"Invalid BundleRef parent for {bref}")

    # Get the attribute from the parent namespace, or fail if not available.
    attr = parent.of.get(bref.attrname)
    if attr is None:
        msg = f"Bundle `{bref.parent.of.name}` has no attribute `{bref.attrname}`"
        failer(msg)
    return attr


def resolve_portref_type(
    pref: PortRef, failer: Callable = fail
) -> Union[Signal, BundleInstance]:
    """Get the `Port` object referred to by `pref`."""

    instantiable = pref.inst._resolved

    if pref.portname in instantiable.ports:
        return instantiable.ports[pref.portname]

    if (
        hasattr(instantiable, "bundle_ports")
        and pref.portname in instantiable.bundle_ports
    ):
        return instantiable.bundle_ports[pref.portname]

    return failer(f"Invalid PortRef {pref}")


def update_ref_deps(ref: Union[PortRef, BundleRef], resolved: Connectable):
    """Update all downstream dependencies on a `Ref` after it has been resolved to `resolved`."""

    # Reconnect all connected ports
    for connected_port in list(ref._connected_ports):
        connected_port.inst.replace(connected_port.portname, resolved)

    # Update all dependent slices and concats
    if hasattr(ref, "_slices"):
        for slice_ in ref._slices:
            slice_.parent = resolved
    if hasattr(ref, "_concats"):
        for concat in ref._concats:
            parts = list(concat.parts)
            parts = [resolved if p is ref else p for p in parts]
            concat.parts = tuple(parts)
