""" 
# Hdl21 Hardware Description Library 
"""

__version__ = "4.0.0"  # NOTE: VLSIR_VERSION


# Before any real importing, ensure we can instantiate non-pydantic types in type-checked dataclasses.
# This `Config` seems to be shared for *all* pydantic types, even when not applied to `BaseModel`.
from pydantic import BaseModel

BaseModel.Config.arbitrary_types_allowed = True

# Internal (python) module aliases, overridden by names such as the `module` decorator function.
from . import module as _module_module
from . import bundle as _bundle_module
from . import external_module as _external_module_module
from . import instance as _instance_module
from . import generator as _generator_module

from . import params
from .params import *

from .instance import *
from .signal import *
from .slice import *
from .concat import *
from .noconn import *
from .external_module import *
from .module import *
from .generator import *
from .bundle import *
from .role import *
from .netlist import *
from .instantiable import *
from .diff_pair import *
from .props import Properties
from .scalar import Scalar
from .literal import Literal

from . import primitives
from .primitives import *

from . import prefix
from .prefix import Prefix, Prefixed

# Import these as modules, but not their contents
from . import generators
from . import sim
from . import pdk
from . import proto
from .proto import to_proto, from_proto

from .walker import HierarchyWalker

from . import elab
from .elab import *

# Update all the forward type-references throughout our many `@datatype`s
from .datatype import _update_forward_refs

_update_forward_refs()
