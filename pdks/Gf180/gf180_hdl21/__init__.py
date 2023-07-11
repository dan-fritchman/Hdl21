from typing import Optional
from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import pdk_logic
from .pdk_logic import *

# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
install: Optional[Install] = None

# And register as a PDK module
register(pdk_logic)
