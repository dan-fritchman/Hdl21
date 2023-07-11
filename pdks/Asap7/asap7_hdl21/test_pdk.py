"""
# Asap7 Hdl21 PDK Plug-In 

Unit Tests
"""

import hdl21 as h
from . import pdk as asap7


def test_default():
    h.pdk.set_default(asap7)
    assert h.pdk.default() is asap7
