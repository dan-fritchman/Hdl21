"""
# SkyWater 130nm OSS PDK Plug-In 

Unit Tests
"""

from io import StringIO
import hdl21 as h
from . import sky130
from .sky130 import modules as s


def test_default():
    h.pdk.set_default(sky130)
    assert h.pdk.default() is sky130


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
    pdk_pkg = sky130.compile(pkg)

    # Import it back into Modules & Namespaces
    ns = h.from_proto(pdk_pkg)
    rt = ns.sky130.test_sky130.hasmos

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
    pkg = sky130.compile(pkg)
    h.netlist(pkg, StringIO(), "spectre")


def test_module1():

    mp = sky130.Sky130MosParams()

    @h.module
    class HasXtors:
        # Instantiate each transistor, with the default parameter values
        ns = s.sky130_fd_pr__nfet_01v8(mp)()
        nl = s.sky130_fd_pr__nfet_01v8_lvt(mp)()
        ps = s.sky130_fd_pr__pfet_01v8(mp)()
        ph = s.sky130_fd_pr__pfet_01v8_hvt(mp)()
