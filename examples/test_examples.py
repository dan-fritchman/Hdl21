"""
# Hdl21 Examples 
## In-line Test Suite

Generally runs the main function of each example "script". 
Check for errors where we can, but largely just check for exceptions.
"""

from .ro import main as ro_main
from .rdac import main as rdac_main
from .encoder import main as encoder_main


def test_ro_example():
    ro_main()


def test_rdac_example():
    rdac_main()


def test_encoder_example():
    encoder_main()
