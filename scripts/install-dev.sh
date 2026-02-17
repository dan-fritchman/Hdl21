# 
# # Install Dependencies
# Dev Mode - VLSIR comes from GitHub 
#

pwd
cd .. 
git clone https://github.com/Vlsir/Vlsir.git
pip install -e ./Vlsir/bindings/python ./Vlsir/VlsirTools ./Vlsir/VlsirDev "./Hdl21[dev]"
# pre-commit install
