"""
# Test Site

Tests which are only valid with a PDK `install` configured, 
generally via a `sitepdks` package. 
"""

import pytest

# Import the site PDKs, or skip all these tests if not available.
sitepdks = pytest.importorskip("sitepdks")

# If that succeeded, import the PDK we want to test.
# It should have a valid `install` attribute.
import {{ cookiecutter.pdk_name }}


def test_installed():
    assert {{ cookiecutter.pdk_name }}.install is not None
