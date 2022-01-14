# Import the VLSIR Schema
from vlsir import circuit_pb2, utils_pb2
from vlsir import circuit_pb2 as circuit
from vlsir.circuit_pb2 import Package

from .to_proto import to_proto
from .from_proto import from_proto
