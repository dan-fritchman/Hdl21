"""
# Hdl21 Pytest Configuration

Primarily adds the simulator-focused options enabled by `VlsirTools`. 
"""


from vlsirtools.pytest import (
    pytest_configure,
    pytest_addoption,
    pytest_collection_modifyitems,
)
