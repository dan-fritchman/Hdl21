"""
# Elaboration 

Defines the primary `elaborate` method used to flesh out an in-memory `Module` or `Generator`. 
Internally defines and uses a number of hierarchical visitor-classes which traverse the hardware hierarchy, 
performing one or more transformation-passes.  
"""

# Std-Lib Imports
from typing import List, Type, TypeVar

# Local imports
from ..datatype import datatype
from .elaboratable import Elaboratable, Elaboratables, is_elaboratable

# Import all the built-in passes, and their abstract base class
from .passes import (
    ElabPass,
    InstBundleElabPass,
    Orphanage,
    ConnTypes,
    BundleFlattener,
    ResolvePortRefs,
    ArrayFlattener,
    SliceResolver,
    MarkModules,
)


ElaboratableType = TypeVar("ElaboratableType", bound=Elaboratables)


@datatype
class Elaborator:
    """
    # Elaborator

    An ordered list of `ElabPass`es.
    Each pass is implemented as a class which inherits from `ElabPass`.
    """

    passes: List[Type[ElabPass]]

    @staticmethod
    def default() -> "Elaborator":
        """Create and return the default Elaborator"""
        return Elaborator(
            passes=[
                #
                Orphanage,
                InstBundleElabPass,
                ResolvePortRefs,
                ConnTypes,
                BundleFlattener,
                ArrayFlattener,
                SliceResolver,
                #
                # A couple repeats
                #
                ConnTypes,
                Orphanage,
                #
                # And final module-marking
                #
                MarkModules,
            ]
        )

    def elaborate(self, top: ElaboratableType) -> ElaboratableType:
        """# Primary elaboration entry point
        Execute each of our `ElabPass`es in sequence."""

        # Check whether we are elaborating a single object or a list thereof
        tops: List[Elaboratable] = top if isinstance(top, List) else [top]

        # Pass `tops` through each of our passes, in order
        for elabpass in self.passes:
            tops = elabpass.elaborate(tops=tops)

        # Extract the single-element case
        if not isinstance(top, List):
            return tops[0]
        return tops


# Set the module-scope elaborator
the_global_elaborator = Elaborator.default()


def elaborate(top: ElaboratableType) -> ElaboratableType:
    """
    # Hdl21 Elaboration

    In-memory elaborates of `Module`s, calls to `Generator`s, and lists thereof.

    Optional `passes` lists the ordered `ElabPass`es to run. By default it runs the order specified by `ElabPass.default`.
    Note the order of passes is important; many depend upon others to have completed before they can successfully run.
    """
    return the_global_elaborator.elaborate(top)


def set_elaborator(e: Elaborator):
    """# Set the global `Elaborator`."""
    if not isinstance(e, Elaborator):
        raise TypeError(f"Invalid ElabPass {e}")
    global the_global_elaborator
    the_global_elaborator = e


def reset_elaborator():
    """# Reset the global `Elaborator` to its default."""
    global the_global_elaborator
    the_global_elaborator = Elaborator.default()


__all__ = [
    "elaborate",
    "Elaborator",
    "set_elaborator",
    "reset_elaborator",
    "Elaboratable",
    "Elaboratables",
    "is_elaboratable",
]
