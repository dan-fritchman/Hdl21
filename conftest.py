"""
# Hdl21 Pytest Configuration

Primarily adds the simulator-focused options enabled by `VlsirTools`. 
"""

import sys
from pydantic import __version__ as pydantic_version

from vlsirtools.pytest import (
    pytest_configure,
    pytest_addoption,
    pytest_collection_modifyitems,
)

# Print some config info: the interpreter version, and the pydantic version
print("Hdl21 PyTest Configuration")
print("Python " + sys.version)
print("Pydantic " + pydantic_version)
