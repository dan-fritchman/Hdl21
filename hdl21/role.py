""""
# Bundle Roles and Role Sets 
"""

# Std Lib Imports
from typing import Optional, List, Dict, Type, TypeVar
from dataclasses import field
from copy import copy
from enum import EnumMeta

# Local Imports
from .datatype import datatype

T = TypeVar("T")


@datatype
class Role:
    """# Bundle Role"""

    name: Optional[str] = None

    def __rmul__(self, num: int) -> List["Role"]:
        """# Right multiplication. Creates `num` copies of this Role."""
        if not isinstance(num, int):
            return NotImplemented
        return [copy(self) for _ in range(num)]


def Roles(num: int) -> List[Role]:
    """# Create `num` new Roles."""
    return [Role() for _ in range(num)]


@datatype
class RoleSet:
    """
    # Bundle Role Set

    Typically used to represent a set of `Role`s that are associated with a `Bundle`.
    """

    name: Optional[str] = None
    inner: Dict[str, Role] = field(default_factory=dict)

    @staticmethod
    def from_enum(enum: EnumMeta):
        """# Convert a standard-library `Enum` class into a `RoleSet`."""
        if not isinstance(enum, EnumMeta):
            raise TypeError(f"Expected EnumMeta, got {enum}")
        return RoleSet(
            name=enum.__name__, inner={role.name: Role(name=role.name) for role in enum}
        )

    @staticmethod
    def from_names(names: List[str]):
        """# Convert a list of role-names into a `RoleSet`."""
        return RoleSet(name=None, inner={name: Role(name=name) for name in names})

    @staticmethod
    def from_list(roles: List[Role]):
        """# Convert a list of `Role`s into a `RoleSet`."""
        return RoleSet(
            name=None, inner={role.name: Role(name=role.name) for role in roles}
        )

    @staticmethod
    def from_dict(roles: Dict[str, Role]):
        """# Convert a dict of `Role`s into a `RoleSet`."""
        return RoleSet(name=None, inner=roles)

    """
    # Special Methods 
    """

    def __getitem__(self, key: str) -> Role:
        """# Get a Role by name."""
        return self.inner[key]

    def __getattr__(self, name: str) -> Role:
        """# Get a Role by name."""
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        return self.inner[name]


def roleset(cls: Type[T]) -> Type[T]:
    """# Decorator to convert an Enum class into a `RoleSet`."""

    return RoleSet.from_enum(cls)


__all__ = ["Role", "Roles", "RoleSet", "roleset"]
