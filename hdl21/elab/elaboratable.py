"""
# Elaborate-able Types 
"""

from typing import Any, List, Union

# Local imports
from ..module import Module
from ..generator import GeneratorCall


# Type short-hand for elaborate-able types
Elaboratable = Union[Module, GeneratorCall]
# (Plural Version)
Elaboratables = Union[Elaboratable, List[Elaboratable]]


def is_elaboratable(obj: Any) -> bool:
    # Function to test this, since `isinstance` doesn't work for `Union`.
    return isinstance(obj, Elaboratable.__args__)
