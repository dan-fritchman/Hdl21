"""
# Slice and Concatenation Resolution 
"""

# Std-Lib Imports
from typing import List, Union

# Local imports
from ...module import Module
from ...signal import Signal
from ...slice import Slice
from ...concat import Concat
from ...portref import PortRef
from ...bundle import BundleRef
from .width import width, Sliceable

# Import the base class
from .base import Elaborator


class SliceResolver(Elaborator):
    """Elaboration pass to resolve slices and concatenations to concrete signals.
    Modifies connections to any nested slices, nested concatenations, or combinations thereof.
    "Full-width" `Slice`s e.g. `sig[:]` are replaced with their parent `Signal`s.

    TODO: `Slice`s with non-unit `step` are converted to `Concat`s."""

    def elaborate_module(self, module: Module) -> Module:
        # All arrays must be flattened before getting here, or fail
        if module.instarrays:
            msg = f"Error attempting to resolve slices on {module} - "
            msg += f"still has Instance Arrays {module.instarrays}"
            raise RuntimeError(msg)

        # Then do the real work, updating any necessary connections on each instance
        for inst in module.instances.values():
            # Update all `Slice` and `Concat` valued connections to remove nested `Slice`s
            for portname, conn in inst.conns.items():
                if isinstance(conn, (Slice, Concat)):
                    resolved = _resolve_sliceable(conn)
                    inst.connect(portname, resolved)
                # All other connection-types (Signals, Interfaces) are fine

        return module


def _resolve_sliceable(conn: Sliceable) -> Sliceable:
    """Resolve a `Sliceable` to flat-concatenation-amenable elements."""
    if isinstance(conn, Signal):
        return conn  # Nothing to do
    if isinstance(conn, Slice):
        return _resolve_slice(conn)
    if isinstance(conn, Concat):
        return _resolve_concat(conn)
    if isinstance(conn, (PortRef, BundleRef)):
        return _resolve_ref(conn)
    raise TypeError(f"Invalid attempt to resolve slicing on {conn}")


def _list_slice(slize: Slice) -> List[Slice]:
    """Internal recursive helper for `resolve_slice`.
    Returns a list of Slices in which each element has a concrete Signal for its parent."""

    # Resolve "full-width" slices to their parent Signals
    if width(slize) == width(slize.parent):
        # Return a single-element list, after resolution
        return [_resolve_sliceable(slize.parent)]

    if isinstance(slize.parent, Signal):
        return [slize]  # Already all good! Just make a one-element list.

    # Do some actual work. Recursively peel off a bit at a time.
    if width(slize) == 1:
        # Base case: slice is one-bit wide. Reach into the parent signal and grab that bit.

        if isinstance(slize.parent, Slice):
            parent = slize.parent  # Note this is also a Slice
            return _list_slice(parent.parent[parent.bot + slize.bot])

        if isinstance(slize.parent, Concat):
            idx = 0  # Find the `part` including our index
            for part in slize.parent.parts:
                if width(part) + idx > slize.bot:
                    return _list_slice(part[slize.bot - idx])
                idx += width(part)
            msg = f"Slice {slize} is out of bounds of Concat {slize.parent}"
            raise RuntimeError(msg)

        raise TypeError(f"Invalid attempt to resolve slicing on {slize}")

    # Otherwise recurse in something like a "cons" pattern, splitting between the first bit and the rest.
    step = slize.step
    if step < 0:  # Negative step, begin from `top`
        first = _list_slice(slize.parent[slize.top])
        rest = slize.parent[slize.top + step : slize.bot : step]
        rest = _list_slice(rest)

    else:  # Positive step, begin from `bot`
        first = _list_slice(slize.parent[slize.bot])
        rest = _list_slice(slize.parent[slize.bot + step : slize.top : step])

    return first + rest


def _resolve_slice(slize: Slice) -> Sliceable:
    """Resolve a `Slice` to one or more with "concrete" `Signal`s as parents.

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
    Such cases create and return a Concatenation."""

    # Break out the slice elements in a list
    ls = _list_slice(slize)
    # And convert to either a single element or Concat
    if len(ls) == 1:  # Resolved to single Slice
        return ls[0]
    elif len(ls) > 1:  # Multiple parts required - concatenate them
        return Concat(*ls)

    raise RuntimeError(f"Error resolving Slice {slize}")


def _resolve_concat(conc: Concat) -> Concat:
    """Resolve a Concatenation into (a) concrete Signals and (b) Slices of concrete Signals.
    Removes nested concatenations and resolves slices along the way."""

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


def _resolve_ref(ref: Union[PortRef, BundleRef]) -> Sliceable:
    """Resolve a reference to a Port or Bundle"""
    if ref.resolved is None:
        raise RuntimeError(f"Unresolved reference {ref}")
    return _resolve_sliceable(ref.resolved)


def _flat_concatable(s: Sliceable) -> bool:
    """Boolean indication of whether `s` is suitable for flattened Concatenations.
    Such objects must be either:
    * (a) A Signal, or
    * (b) A Slice into a Signal
    Notable exceptions include Concats and nested Slices of Concats and other Slices."""
    return isinstance(s, Signal) or (
        isinstance(s, Slice) and isinstance(s.parent, Signal)
    )
