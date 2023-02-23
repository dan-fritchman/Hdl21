"""
# {{cookiecutter.repo_name}} 
## {{cookiecutter.pdk_name}} Hdl21 PDK Package
"""

from pathlib import Path
from typing import Optional
from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import pdk
from .pdk import *


# And register as a PDK module
register(pdk)

# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
install: Optional[Install] = None

# Provide a `resources` path to our built-in non-Python data
# This enables usage along the lines of
# `mypdk.resources / "a_file.txt"
resources = Path(__file__).parent / "resources"
