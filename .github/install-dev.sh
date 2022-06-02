# 
# # Install Dependencies
# Dev Mode - VLSIR comes from GitHub 
#

pwd
cd .. 
git clone https://github.com/dan-fritchman/Vlsir.git
cd Vlsir/bindings/python 
pip install -e .
cd ../../VlsirTools
pip install -e .
cd ../../Hdl21
pip install -e ".[dev]"

