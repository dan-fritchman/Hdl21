"""
# Elaborate-able Types 
"""

from typing import Any, List, Union, get_args
from types import SimpleNamespace

# Local imports
from ..module import Module
from ..generator import Generator, GeneratorCall


# Type short-hand for elaborate-able types
Elabable = Union[Module, Generator, GeneratorCall]
# (Plural Version)
Elabables = Union[Elabable, List[Elabable], SimpleNamespace]


def is_elabable(obj: Any) -> bool:
    # Function to test this, since `isinstance` doesn't work for `Union`.
    return isinstance(obj, get_args(Elabable))
