"""
# Hdl21 PDK Sample 

An entirely fictitious process-technology, 
written solely as a demonstration of an `hdl21.pdk` plug-in package. 
"""

from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import sample_pdk

# And register as a PDK module
register(sample_pdk)
