"""
# Qualified Names 

Helpers for uniquely identifying a Module or ExternalModule, 
given their native language (Python) has hierarchical namespaces, 
and many of their import/ export languages (e.g. Verilog, netlists) do not.
"""


from typing import Any, Optional, Union, TypeVar, Type


def qualname(mod: Union["Module", "ExternalModule", "Generator"]) -> Optional[str]:
    """# Qualified Name
    Helper for exporting. Returns a module's path-qualified name.
    This is generally one of a few things:
    * If "normally" defined via Python code, it's the Python module path plus the module name.
    * If *imported*, it's the path inferred during import."""

    if getattr(mod, "_importpath", None) is not None:
        # Imported. Return the period-separated import path.
        return ".".join(mod._importpath)

    if mod.name is None:
        # Unnamed. Return None.
        return None

    if mod._source_info.pymodule is None:
        # Defined in a non-Python context. Return the Module's name, without any path qualifiers.
        return mod.name

    # Defined the old fashioned way. Use the Python module name.
    return mod._source_info.pymodule.__name__ + "." + mod.name


T = TypeVar("T")


def qualname_magic_methods(cls: Type[T]) -> Type[T]:
    """Decorator to add the 'use qualname for equality, hashing, and pickling'
    magic methods to a class."""

    def __eq__(self, other: "Self") -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        if self.name is None or other.name is None:
            raise RuntimeError(f"Cannot invoke equality on unnamed {type(self)} {self}")
        return qualname(self) == qualname(other)

    def __hash__(self):
        if self.name is None:
            raise RuntimeError(f"Cannot invoke hashing on unnamed {type(self)} {self}")
        return hash(qualname(self))

    def __getstate__(self):
        if self.name is None:
            raise RuntimeError(f"Cannot invoke pickling on unnamed {type(self)} {self}")
        return qualname(self)

    cls.__eq__ = __eq__
    cls.__hash__ = __hash__
    cls.__getstate__ = __getstate__
    return cls
