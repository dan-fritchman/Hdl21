"""
# Hdl21 ASAP7 PDK 
"""

from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import asap7

# And register as a PDK module
register(asap7)
