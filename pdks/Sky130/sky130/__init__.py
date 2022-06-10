from typing import Optional
from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import sky130
from .sky130 import modules, Sky130MosParams, Sky130Walker, Install


# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
install: Optional[Install] = None

# And register as a PDK module
register(sky130)
