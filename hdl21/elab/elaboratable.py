"""
# Elaborate-able Types 

More specifically, things that can be *the top level* of an elaboration process. 
Sets the type-bounds on primary arguments to `elaborate` and related functions. 
"""

from typing import Any, List, Union

# Local imports
from ..module import Module
from ..primitives import PrimitiveCall
from ..external_module import ExternalModuleCall


# Type short-hands for elaborate-able types
# NOTE: this is identical to `Instantiable`.
# Although maybe some day it won't be?
Elaboratable = Union[Module, ExternalModuleCall, PrimitiveCall]
# (Plural Version)
Elaboratables = Union[Elaboratable, List[Elaboratable]]


def is_elaboratable(obj: Any) -> bool:
    # Function to test this, since `isinstance` doesn't work for `Union`.
    return isinstance(obj, Elaboratable.__args__)
