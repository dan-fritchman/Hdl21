"""
# Hdl21 PDK Sample 

An entirely fictitious process-technology, 
written solely as a demonstration of an `hdl21.pdk` plug-in package. 
"""

from pathlib import Path
from typing import Optional
from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import pdk
from .pdk import *


# And register as a PDK module
register(pdk)

# Provide a `resources` path to our non-Python data
# This enables usage along the lines of
# `sample_pdk.resources / "a_file.txt"
resources = Path(__file__).parent / "resources"

# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
# Unlike most PDK pacakges, this sample provides a default `Install`,
# as it has a very small amount of non-Python data,
# which is tracked in this repository.
install: Optional[Install] = Install(models=resources / "models.sp")
