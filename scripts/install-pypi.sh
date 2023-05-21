# 
# # Install Dependencies
# PyPi Mode - 
# Everything, notably including VLSIR, comes from PyPi
#

pip install --pre --editable ".[dev]"
pip install pre-commit
pre-commit install
