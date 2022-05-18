from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import sky130
from .sky130 import modules, Sky130MosParams, Sky130Walker, Install

# And register as a PDK module
register(sky130)
