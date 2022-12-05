"""
# Hdl21 Sample PDK 

Unit Tests
"""

import hdl21 as h
from io import StringIO
from . import pdk as sample_pdk


def test_default():
    h.pdk.set_default(sample_pdk)
    assert h.pdk.default() is sample_pdk


def mosmodule():
    # Create a simple Module with each of the default-param Mos types
    hasmos = h.Module(name="hasmos")
    z = hasmos.z = h.Signal()
    hasmos.n = h.Nmos(h.MosParams())(d=z, g=z, s=z, b=z)
    hasmos.p = h.Pmos(h.MosParams())(d=z, g=z, s=z, b=z)

    # Checks on the initial Module
    assert isinstance(hasmos.n, h.Instance)
    assert isinstance(hasmos.p, h.Instance)
    assert isinstance(hasmos.n.of, h.PrimitiveCall)
    assert isinstance(hasmos.p.of, h.PrimitiveCall)

    return hasmos


def test_compile():
    hasmos = mosmodule()

    # Compile it for the PDK
    sample_pdk.compile(hasmos)

    # And check what came back
    assert isinstance(hasmos.n, h.Instance)
    assert isinstance(hasmos.p, h.Instance)
    assert isinstance(hasmos.n.of, h.ExternalModuleCall)
    assert isinstance(hasmos.p.of, h.ExternalModuleCall)
    assert isinstance(hasmos.n.of.params, sample_pdk.SamplePdkMosParams)
    assert isinstance(hasmos.p.of.params, sample_pdk.SamplePdkMosParams)


def test_netlist():
    hasmos = mosmodule()

    # Netlist it for the PDK
    sample_pdk.compile(hasmos)
    h.netlist(hasmos, StringIO(), fmt="spice")
    h.netlist(hasmos, StringIO(), fmt="spectre")
    h.netlist(hasmos, StringIO(), fmt="verilog")
