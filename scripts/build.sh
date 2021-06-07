
# Python Protobuf Compilation
protoc -I=./hdl21/proto --python_out=./hdl21/proto ./hdl21/proto/*.proto
# Sadly protoc doesn't seem to know how Python3 imports work
2to3 -wn -f import hdl21/proto/*.py
