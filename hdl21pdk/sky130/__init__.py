import hdl21pdk

# Grab our primary PDK-definition module
from . import sky130

# And register as a PDK module
hdl21pdk.register(sky130)
