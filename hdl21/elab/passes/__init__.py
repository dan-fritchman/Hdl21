""" 
# Elaboration Passes

Recursive walkers of Hdl21 hierarchies which perform the mechanics of elaboration. 
"""

# Import the abstract base class for typing guards
from .base import ElabPass

# And all the built-in passes
from .inst_bundles import InstBundleElabPass
from .slices import SliceResolver
from .orphanage import Orphanage
from .arrays import ArrayFlattener
from .portrefs import ResolvePortRefs
from .conntypes import ConnTypes
from .flatten_bundles import BundleFlattener
from .mark_modules import MarkModules
