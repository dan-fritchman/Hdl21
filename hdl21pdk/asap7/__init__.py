import hdl21pdk

# Grab our primary PDK-definition module
from . import asap7

# And register as a PDK module
hdl21pdk.register(asap7)
