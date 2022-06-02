"""
# Orphan-Testing (Orphanage) Elaborator
"""

# Local imports
from ...module import Module

# Import the base class
from .base import Elaborator


class Orphanage(Elaborator):
    """ # Orphan-Checking Elaborator Pass 

    Ensures each Module-attribute is "parented" by the `Module` which holds it. 
    Errant cases can come up for code such as: 
    
    ```
    m1 = h.Module(name='m1')
    m1.s = h.Signal() # Signal `s` is now "parented" by `m1`

    m2 = h.Module(name='m2')
    m2.y = m1.s # Now `s` has been "orphaned" (or perhaps "cradle-robbed") by `m2`
    ```

    This essentially boils down to the difference between Python's native reference-semantics, 
    and `hdl21.Module`'s notion of "owning" its attributes. 
    Note other *references* to Module attributes are allowed, such as: 

    ```
    m1 = h.Module(name='m1')
    m1.s = h.Signal() # Signal `s` is now "parented" by `m1`

    my_favorite_signals = { "from_m1" : m1.s }
    ```

    Here the dictionary `my_favorite_signals` retains a reference to Signal `s`. 
    This does not generate an orphan-error complaint, so long as Module-level ownership is unique and unambiguous. 

    The orphan-test is very simple: each Module-attribute is annotated with a `_parent_module` member 
    upon insertion into the Module namespace. 
    Orphan-testing simply requires that for each attribute, this member is identical to the parent Module. 
    A `RuntimeError` is raised if orphaned attributes are detected. 
    Otherwise each Module is returned unchanged.
    """

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate a Module """
        # Check each attribute in the module namespace for orphanage.
        for attr in module.namespace.values():
            if attr._parent_module is not module:
                msg = f"Orphanage: Module {module} attribute {attr} is actually owned by another Module {attr._parent_module}!"
                raise RuntimeError(msg)
        # Checks out! Return the module unchanged.
        return module
