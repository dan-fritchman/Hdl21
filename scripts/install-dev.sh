# 
# # Install Dependencies
# Dev Mode - VLSIR comes from GitHub 
#

pwd
cd .. 
git clone https://github.com/Vlsir/Vlsir.git
cd Vlsir/bindings/python 
pip install -e .
cd ../../VlsirTools
pip install -e .
cd ../../Hdl21
pip install -e ".[dev]"
pip install pre-commit
pre-commit install
