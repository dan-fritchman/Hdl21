""" 
# Elaborator Class(es)

Recursive walkers of Hdl21 hierarchies which perform the mechanics of elaboration. 
"""

from .generators import GeneratorElaborator
from .inst_bundles import InstBundleElaborator
from .slices import SliceResolver
from .orphanage import Orphanage
from .arrays import ArrayFlattener
from .portrefs import ResolvePortRefs
from .conntypes import ConnTypes
from .flatten_bundles import BundleFlattener
from .mark_modules import MarkModules
