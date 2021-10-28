""" 
# Hdl21 Hardware Description Library 
"""

__version__ = "0.1.1"


# Before any real importing, ensure we can instantiate non-pydantic types in type-checked dataclasses.
# This `Config` seems to be shared for *all* pydantic types, even when not applied to `BaseModel`.
from pydantic import BaseModel

BaseModel.Config.arbitrary_types_allowed = True

from .params import *
from .instance import *
from .signal import *
from .module import *
from .generator import *
from .generators import *
from .primitives import *
from .interface import *
from .netlist import *
from .elab import *
from .walker import HierarchyWalker
from .instantiable import *

from . import proto
from .proto import to_proto, from_proto

