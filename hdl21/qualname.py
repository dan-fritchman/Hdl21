"""
# Qualified Names 

Helpers for uniquely identifying a Module or ExternalModule, 
given their native language (Python) has hierarchical namespaces, 
and many of their import/ export languages (e.g. Verilog, netlists) do not.
"""

from typing import Optional, Union, List

# Type alias of the types that have a qualified path.
HasQualPath = Union["Module", "ExternalModule", "Generator"]


def qualpath(mod: HasQualPath) -> Optional[List[str]]:
    """# Qualified Path
    Helper for exporting. Returns a module's definition path.
    This is generally one of a few things:
    * If "normally" defined via Python code, it's the Python module path plus the module name.
    * If *imported*, it's the path inferred during import."""

    if getattr(mod, "_importpath", None) is not None:
        # Imported. Return the period-separated import path.
        return mod._importpath

    if mod.name is None:
        # Unnamed. Return None.
        return None

    if mod._source_info.pymodule is None:
        # Defined outside a Python module, e.g. in a call to `exec`, a notebook cell, or a `python -c` string.
        # Return its name without any path qualifiers.
        return [mod.name]

    # Defined the old fashioned way. Use the Python module name.
    return mod._source_info.pymodule.__name__.split(".") + [mod.name]


def qualname(mod: HasQualPath) -> Optional[str]:
    """# Qualified Name
    Helper for exporting. Returns a module's path-qualified name.
    If `mod` has a qualified path as determined by `qualpath`, returns it
    joined together by the Python-conventional path-separator "."."""

    qpath = qualpath(mod)
    if qpath is None:
        return None
    return ".".join(qpath)
