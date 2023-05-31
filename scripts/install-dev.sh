# 
# # Install Dependencies
# Dev Mode - VLSIR comes from GitHub 
#

pwd
cd .. 
git clone https://github.com/Vlsir/Vlsir.git
cd Vlsir/bindings/python 
pip install -e ".[dev]"
cd ../../VlsirTools
pip install -e ".[dev]"
cd ../../Hdl21
pip install -e ".[dev]"
# pre-commit install
