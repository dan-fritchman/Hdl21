"""
# Hdl21 PDK Sample 

Demonstration of an `hdl21.pdk` plug-in package. 
Not a working or existing process technology. 
"""

from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import sample_pdk

# And register as a PDK module
register(sample_pdk)
