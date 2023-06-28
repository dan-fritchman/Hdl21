"""
# Hdl21 Examples 
## In-line Test Suite

Generally runs the main function of each example "script". 
Check for errors where we can, but largely just check whether they generate exceptions. 
Importing these functions with names that begin with `test_` gets them picked up by pytest. 
"""

from .ro import main as test_ro
from .rdac import main as test_rdac
from .encoder import main as test_encoder
from .mos_sim import main as test_mos_sim
from .diff_ota import main as test_diff_ota
from .idac import main as test_idac
from .bundles import main as test_bundles
