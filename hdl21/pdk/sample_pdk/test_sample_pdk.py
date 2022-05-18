"""
# Hdl21 Sample PDK 

Unit Tests
"""

import hdl21 as h
from io import StringIO
from . import sample_pdk


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
    pkg = h.to_proto(hasmos)
    pdk_pkg = sample_pdk.compile(pkg)

    # Import it back into Modules & Namespaces
    ns = h.from_proto(pdk_pkg)
    rt = ns.hdl21.pdk.sample_pdk.test_sample_pdk.hasmos

    # And check what came back
    assert isinstance(rt.n, h.Instance)
    assert isinstance(rt.p, h.Instance)
    assert isinstance(rt.n.of, h.ExternalModuleCall)
    assert isinstance(rt.p.of, h.ExternalModuleCall)
    assert isinstance(rt.n.of.params, dict)
    assert isinstance(rt.p.of.params, dict)


def test_netlist():
    hasmos = mosmodule()

    # Netlist it for the PDK
    pkg = h.to_proto(hasmos)
    pkg = sample_pdk.compile(pkg)
    h.netlist(pkg, StringIO(), "spectre")
