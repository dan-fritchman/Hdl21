""" 
# Hdl21 Unit Tests

* Exporting to VLSIR 
  * Ultimately to EDA formats 
* Importing back from VLSIR
"""

import sys, pytest
from io import StringIO
from types import SimpleNamespace
from textwrap import dedent

# Import the PUT (package under test)
import hdl21 as h
import vlsir


@pytest.mark.xfail(reason="#1 https://github.com/dan-fritchman/Hdl21/issues/1")
def test_export_strides():
    """Test exporting connections with non-unit Slice-strides"""

    c = h.Module(name="c")
    c.p = h.Input(width=2)

    p = h.Module(name="p")
    p.s = h.Signal(width=20)
    p.c = c(p=p.s[::10])  # Connect two of the 20 bits, with stride 10

    h.netlist(h.to_proto(p), sys.stdout, fmt="verilog")


def test_prim_proto1():
    # Test round-tripping primitives through proto

    @h.module
    class HasPrims:
        p = h.Signal()
        n = h.Signal()

        # Wire up a bunch of two-terminal primitives in parallel
        _rp = h.R.Params(r=50)
        r = h.Resistor(_rp)(p=p, n=n)
        _cp = h.C.Params(c=1e-12)
        c = h.Capacitor(_cp)(p=p, n=n)
        _lp = h.L.Params(l=1e-15)
        l = h.Inductor(_lp)(p=p, n=n)
        _dp = h.D.Params()
        d = h.Diode(_dp)(p=p, n=n)
        _sp = h.Short.Params()
        s = h.Short(_sp)(p=p, n=n)

    ppkg = h.to_proto(HasPrims)

    assert isinstance(ppkg, vlsir.circuit.Package)
    assert len(ppkg.modules) == 1
    assert ppkg.domain == ""

    # Check the proto-Module
    pm = ppkg.modules[0]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.HasPrims"
    assert len(pm.ports) == 0
    assert len(pm.signals) == 2
    assert len(pm.instances) == 5
    assert len(pm.parameters) == 0
    for inst in pm.instances:
        assert isinstance(inst, vlsir.circuit.Instance)
        assert inst.module.WhichOneof("to") == "external"
        assert inst.module.external.domain in ["vlsir.primitives", "hdl21.primitives"]

    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    ns = ns.hdl21.tests.test_exports
    assert isinstance(ns, SimpleNamespace)
    assert hasattr(ns, "HasPrims")
    HasPrims = ns.HasPrims
    assert isinstance(HasPrims, h.Module)
    assert len(HasPrims.ports) == 0
    assert len(HasPrims.signals) == 2
    assert len(HasPrims.instances) == 5
    for inst in HasPrims.instances.values():
        assert isinstance(inst._resolved, h.primitives.PrimitiveCall)


def test_ideal_primitives():
    # Test round-tripping ideal primitives

    @h.module
    class HasPrims:
        p = h.Signal()
        n = h.Signal()
        p2 = h.Signal()
        n2 = h.Signal()

        # Wire up a bunch of two-terminal primitives in parallel
        _rp = h.R.Params(r=50)
        r = h.Resistor(_rp)(p=p, n=n)
        _cp = h.C.Params(c=1e-12)
        c = h.Capacitor(_cp)(p=p, n=n)
        _lp = h.L.Params(l=1e-15)
        l = h.Inductor(_lp)(p=p, n=n)
        _dp = h.D.Params()
        d = h.Diode(_dp)(p=p, n=n)
        _sp = h.Short.Params()
        s = h.Short(_sp)(p=p, n=n)
        _vdc = h.Vdc.Params(dc=0 * h.prefix.m, ac=0 * h.prefix.m)
        vdc = h.Vdc(_vdc)(p=p, n=n)
        _vpu = h.Vpulse.Params(
            delay=0 * h.prefix.m,
            v1=0 * h.prefix.m,
            v2=0 * h.prefix.m,
            period=0 * h.prefix.m,
            rise=0 * h.prefix.m,
            fall=0 * h.prefix.m,
            width=0 * h.prefix.m,
        )
        vpu = h.Vpulse(_vpu)(p=p, n=n)
        _vsin = h.Vsin.Params(
            voff=0 * h.prefix.m,
            vamp=0 * h.prefix.m,
            freq=0 * h.prefix.m,
            td=0 * h.prefix.m,
            phase=0 * h.prefix.m,
        )
        vsin = h.Vsin(_vsin)(p=p, n=n)
        _idc = h.Idc.Params(dc=0 * h.prefix.m)
        idc = h.Idc(_idc)(p=p, n=n)
        _vcvs = h.Vcvs.Params(gain=1 * h.prefix.m)
        vcvs = h.Vcvs(_vcvs)(p=p, n=n, cp=p2, cn=n2)
        _ccvs = h.Ccvs.Params(gain=1 * h.prefix.m)
        ccvs = h.Ccvs(_ccvs)(p=p, n=n, cp=p2, cn=n2)
        _vccs = h.Vccs.Params(gain=1 * h.prefix.m)
        vccs = h.Vccs(_vccs)(p=p, n=n, cp=p2, cn=n2)
        _cccs = h.Cccs.Params(gain=1 * h.prefix.m)
        cccs = h.Cccs(_cccs)(p=p, n=n, cp=p2, cn=n2)

    ppkg = h.to_proto(HasPrims)
    ns = h.from_proto(ppkg)


def test_proto1():
    # First Proto-export test

    m = h.Module(name="TestProto1")
    ppkg = h.to_proto(m)
    assert isinstance(ppkg, vlsir.circuit.Package)
    assert len(ppkg.modules) == 1
    assert ppkg.domain == ""
    pm = ppkg.modules[0]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.TestProto1"
    assert len(pm.ports) == 0
    assert len(pm.instances) == 0
    assert len(pm.parameters) == 0


def test_proto2():
    # Proto-export test with some hierarchy

    Child1 = h.Module(name="Child1")
    Child1.inp = h.Input(width=8)
    Child1.out = h.Output()
    Child2 = h.Module(name="Child2")
    Child2.inp = h.Input()
    Child2.out = h.Output(width=8)
    TestProto2 = h.Module(name="TestProto2")
    TestProto2.c1 = Child1()
    TestProto2.c2 = Child2()
    TestProto2.c2(inp=TestProto2.c1.out, out=TestProto2.c1.inp)

    ppkg = h.to_proto(TestProto2)

    assert isinstance(ppkg, vlsir.circuit.Package)
    assert len(ppkg.modules) == 3
    assert ppkg.domain == ""

    # Check the first Module in, Child1
    pm = ppkg.modules[0]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.Child1"
    assert len(pm.ports) == 2
    assert len(pm.signals) == 2
    assert len(pm.instances) == 0
    assert len(pm.parameters) == 0

    # Check the second Module in, Child2
    pm = ppkg.modules[1]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.Child2"
    assert len(pm.ports) == 2
    assert len(pm.signals) == 2
    assert len(pm.instances) == 0
    assert len(pm.parameters) == 0

    # And check the parent module
    pm = ppkg.modules[2]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.TestProto2"
    assert len(pm.ports) == 0
    assert len(pm.signals) == 2
    assert len(pm.instances) == 2
    assert len(pm.parameters) == 0


def test_proto3():
    # Proto-export test with some slicing and concatenation

    M1 = h.Module(name="M1")
    M1.p8 = h.Inout(width=8)
    M1.p1 = h.Inout(width=1)

    M2 = h.Module(name="M2")
    M2.s = h.Signal(width=4)
    M2.i = M1()
    M2.i(p1=M2.s[0])
    M2.i(p8=h.Concat(M2.s, h.Concat(M2.s[0], M2.s[1]), M2.s[2:4]))

    ppkg = h.to_proto(M2, domain="test_proto3")

    assert isinstance(ppkg, vlsir.circuit.Package)
    assert len(ppkg.modules) == 2
    assert ppkg.domain == "test_proto3"

    # Check the child module
    pm = ppkg.modules[0]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.M1"
    assert len(pm.ports) == 2
    assert len(pm.signals) == 2
    assert len(pm.instances) == 0
    assert len(pm.parameters) == 0

    # And check the parent module
    pm = ppkg.modules[1]
    assert isinstance(pm, vlsir.circuit.Module)
    assert pm.name == "hdl21.tests.test_exports.M2"
    assert len(pm.ports) == 0
    assert len(pm.signals) == 1
    assert len(pm.instances) == 1
    assert len(pm.parameters) == 0

    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    ns = ns.hdl21.tests.test_exports
    assert isinstance(ns, SimpleNamespace)
    assert isinstance(ns.M1, h.Module)
    assert len(ns.M1.ports) == 2
    assert len(ns.M1.signals) == 0
    assert len(ns.M1.instances) == 0

    assert isinstance(M2, h.Module)
    assert len(M2.ports) == 0
    assert len(M2.signals) == 1
    assert len(M2.instances) == 1
    assert "s" in M2.signals
    assert "i" in M2.instances
    inst = M2.i
    assert isinstance(inst.conns["p1"], h.Slice)
    assert inst.conns["p1"].parent is M2.s
    assert inst.conns["p1"].top == 1
    assert inst.conns["p1"].bot == 0
    assert inst.conns["p1"].width == 1
    assert isinstance(inst.conns["p8"], h.Concat)
    assert len(inst.conns["p8"].parts) == 4
    assert inst.conns["p8"].parts[0] is M2.s
    assert isinstance(inst.conns["p8"].parts[0], h.Signal)
    assert isinstance(inst.conns["p8"].parts[1], h.Slice)
    assert isinstance(inst.conns["p8"].parts[2], h.Slice)
    assert isinstance(inst.conns["p8"].parts[3], h.Slice)


def test_proto_roundtrip():
    # Test protobuf round-tripping

    # Create an empty (named) Module
    M1 = h.Module(name="M1")

    # Protobuf round-trip it
    ppkg = h.to_proto(M1)
    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    ns = ns.hdl21.tests.test_exports
    assert isinstance(ns, SimpleNamespace)
    assert isinstance(ns.M1, h.Module)
    assert len(ns.M1.signals) == 0
    assert len(ns.M1.ports) == 0
    assert len(ns.M1.instances) == 0


def test_proto_roundtrip2():

    # Create a child/leaf Module
    M1 = h.Module(name="M1")
    M1.i = h.Input()
    M1.o = h.Output()
    M1.p = h.Port()

    # Create an instantiating parent-module
    M2 = h.Module(name="M2")
    M2.i = h.Input()
    M2.o = h.Output()
    M2.p = h.Port()
    M2.s = h.Signal()

    # Add a few instances of it
    M2.i0 = M1()
    M2.i1 = M1()
    M2.i2 = M1()
    M2.i0(i=M2.i, o=M2.i1.i, p=M2.p)
    M2.i1(i=M2.i0.o, o=M2.s, p=M2.p)
    M2.i2(i=M2.s, o=M2.o, p=M2.p)

    # Protobuf round-trip it
    ppkg = h.to_proto(M2)
    ns = h.from_proto(ppkg)

    # And check all kinda stuff about what comes back
    assert isinstance(ns, SimpleNamespace)
    M1 = ns.hdl21.tests.test_exports.M1
    M2 = ns.hdl21.tests.test_exports.M2
    assert isinstance(M1, h.Module)
    assert isinstance(M2, h.Module)

    assert len(M1.signals) == 0
    assert len(M1.ports) == 3
    assert "i" in M1.ports
    assert M1.i.direction == h.signal.PortDir.INPUT
    assert M1.i.vis == h.signal.Visibility.PORT
    assert "o" in M1.ports
    assert M1.o.direction == h.signal.PortDir.OUTPUT
    assert M1.o.vis == h.signal.Visibility.PORT
    assert "p" in M1.ports
    assert M1.p.direction == h.signal.PortDir.NONE
    assert M1.p.vis == h.signal.Visibility.PORT
    assert len(M1.instances) == 0

    assert len(M2.instances) == 3
    for i in M2.instances.values():
        assert i.of is M1
        assert i.conns["p"] is M2.p
    assert len(M2.ports) == 3
    assert len(M2.signals) == 2
    assert "s" in M2.signals
    assert "i0_o" in M2.signals


def test_netlist_fmts():
    """Test netlisting basic types to several formats"""

    @h.module
    class Bot:
        s = h.Input(width=3)
        p = h.Output()

    @h.module
    class Top:
        s = h.Signal(width=3)
        p = h.Output()
        b = Bot(s=s, p=p)

    # Convert to proto
    ppkg = h.to_proto(Top)
    assert len(ppkg.modules) == 2
    assert ppkg.modules[0].name == "hdl21.tests.test_exports.Bot"
    assert ppkg.modules[1].name == "hdl21.tests.test_exports.Top"

    # Convert the proto-package to a netlist
    nl = StringIO()
    h.netlist(ppkg, nl, fmt="spectre")
    nl = nl.getvalue()

    # Basic checks on its contents
    assert "subckt Bot" in nl
    assert "s_2 s_1 s_0 p" in nl
    assert "subckt Top" in nl
    assert "b\n" in nl
    assert "( s_2 s_1 s_0 p )" in nl
    assert "+ p" in nl
    assert "+  Bot " in nl

    # Convert the proto-package to another netlist format
    nl = StringIO()
    h.netlist(ppkg, nl, fmt="verilog")
    nl = nl.getvalue()

    # Basic checks on its contents
    assert "module Bot" in nl
    assert "input wire [2:0] s," in nl
    assert "output wire p" in nl
    assert "endmodule // Bot" in nl
    assert "module Top" in nl
    assert ".s(s)" in nl
    assert ".p(p)" in nl
    assert "endmodule // Top" in nl

    nl = StringIO()
    h.netlist(ppkg, nl, fmt="spice")
    nl = nl.getvalue()
    assert ".SUBCKT Bot \n+ s_2 s_1 s_0 p" in nl
    assert ".SUBCKT Top \n+ p" in nl
    assert "xb \n+ s_2 s_1 s_0 p \n+ Bot" in nl


def test_spice_netlister():
    from hdl21.prefix import e

    @h.module
    class DUT:
        a = h.Input(width=5)
        b = h.Output(width=5)
        res = h.IdealResistor(h.ResistorParams(r=10 * e(3)))(p=a[0], n=b[0])
        cap = h.IdealCapacitor(h.IdealCapacitorParams(c=10 * e(-12)))(p=a[1], n=b[1])
        ind = h.IdealInductor(h.IdealInductorParams(l=10 * e(-9)))(p=a[2], n=b[2])

    ppkg = h.to_proto(DUT)
    nl = StringIO()
    h.netlist(ppkg, nl, fmt="spice")

    nl = nl.getvalue()
    assert ".SUBCKT DUT" in nl
    assert "+ a_4 a_3 a_2 a_1 a_0 b_4 b_3 b_2 b_1 b_0" in nl
    assert "rres" in nl
    assert "+ a_0 b_0" in nl
    assert "+ 10K" in nl
    assert "ccap" in nl
    assert "+ a_1 b_1" in nl
    assert "+ 10p" in nl
    assert "lind" in nl
    assert "+ a_2 b_2" in nl
    assert "+ 10n" in nl


def test_bad_proto_naming():
    """Test some naming cases which are alright in Python,
    but generate naming conflicts in serialization.
    Generally these boil down to "same `Module`-names in same Python module"."""

    # Create a naming conflict between Module definitions
    Ma1 = h.Module(name="Ma")
    Ma2 = h.Module(name="Ma")

    @h.module
    class MaParent:
        ma1 = Ma1()
        ma2 = Ma2()

    h.elaborate(MaParent)
    with pytest.raises(RuntimeError):
        h.to_proto(MaParent)

    # Do the same via some functions that should be generators
    def m1():
        return h.Module(name="Ma")

    def m2():
        return h.Module(name="Ma")

    @h.module
    class MaParent:
        ma1 = m1()()
        ma2 = m2()()

    h.elaborate(MaParent)
    with pytest.raises(RuntimeError):
        h.to_proto(MaParent)


def test_generator_recall():
    """Test multi-calling generators"""

    @h.generator
    def CallMeTwice(_: h.HasNoParams) -> h.Module:
        return h.Module()

    @h.module
    class Caller:
        m1 = CallMeTwice(h.NoParams)()
        m2 = CallMeTwice(h.NoParams)()

    # Convert to proto
    ppkg = h.to_proto(Caller)
    assert len(ppkg.modules) == 2
    assert ppkg.modules[0].name == "hdl21.tests.test_exports.CallMeTwice"
    assert ppkg.modules[1].name == "hdl21.tests.test_exports.Caller"

    # Convert the proto-package to a netlist, and run some (very basic) checks
    nl = StringIO()
    h.netlist(ppkg, nl)
    nl = nl.getvalue()
    assert "CallMeTwice" in nl
    assert "Caller" in nl

    # Round-trip back from Proto to Modules
    rt = h.from_proto(ppkg)
    ns = rt.hdl21.tests.test_exports
    assert isinstance(ns.Caller, h.Module)
    assert isinstance(getattr(ns, "CallMeTwice"), h.Module)


def test_rountrip_external_module():
    """Test round-tripping `ExternalModule`s between Hdl21 and VLSIR Proto"""

    @h.paramclass
    class P:  # Our ExternalModule's parameter-type
        a = h.Param(dtype=int, desc="a", default=1)
        b = h.Param(dtype=str, desc="b", default="two")

    E = h.ExternalModule(name="E", port_list=[], paramtype=P)

    @h.module
    class HasE:
        e = E(P())()

    exported = h.to_proto(HasE)
    imported = h.from_proto(exported)
    h.to_proto(imported.hdl21.tests.test_exports.HasE)


def test_module_with_no_python_module():
    # Issue #48 https://github.com/dan-fritchman/Hdl21/issues/48
    exec("import hdl21 as h; h.to_proto(h.Module(name='not_in_a_pymodule'))")
