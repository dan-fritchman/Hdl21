"""
# Unit Tests
"""

import hdl21 as h

from . import pdk


def test_set_default():
    """Test that we can set the default PDK"""

    h.pdk.set_default(pdk)
    assert h.pdk.default() is pdk
