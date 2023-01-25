""" 
# Hdl21 Unit Tests 
"""

import copy, pytest
from enum import Enum, EnumMeta, auto

import hdl21 as h


def test_version():
    assert h.__version__ == "2.0.dev0"


def test_module1():
    """Initial Module Test"""

    @h.module
    class M1:
        a = h.Input()
        b = h.Output()
        c = h.Inout()
        d = h.Port()
        e = h.Signal()
        f = h.Signal()

    assert isinstance(M1, h.Module)
    assert isinstance(M1.ports, dict)
    assert isinstance(M1.signals, dict)
    assert isinstance(M1.instances, dict)
    assert "a" in M1.ports
    assert "a" not in M1.signals
    assert "b" in M1.ports
    assert "b" not in M1.signals
    assert "c" in M1.ports
    assert "c" not in M1.signals
    assert "d" in M1.ports
    assert "d" not in M1.signals
    assert "e" in M1.signals
    assert "e" not in M1.ports
    assert "f" in M1.signals
    assert "f" not in M1.ports
    assert M1.e is not M1.f


def test_module2():
    @h.module
    class M1:
        s = h.Input()

    @h.module
    class M2:
        q = h.Signal()
        i = M1(s=q)

    assert isinstance(M1, h.Module)
    assert isinstance(M2, h.Module)
    assert isinstance(M1.ports["s"], h.Signal)
    assert isinstance(M2.signals["q"], h.Signal)
    assert isinstance(M2.instances["i"], h.Instance)

    # Test the getattr magic for signals, ports, and instances
    assert isinstance(M2.i, h.Instance)
    assert M2.instances["i"] is M2.i
    assert isinstance(M2.q, h.Signal)
    assert M2.signals["q"] is M2.q
    assert isinstance(M1.s, h.Signal)
    assert M1.ports["s"] is M1.s


def test_generator1():
    @h.paramclass
    class MyParams:
        w = h.Param(dtype=int, desc="five", default=5)

    @h.generator
    def gen1(params: MyParams) -> h.Module:
        m = h.Module()
        m.i = h.Input(width=params.w)
        return m

    m = h.elaborate(gen1(MyParams(w=3)))

    assert m.name == "gen1(w=3)"
    assert isinstance(m.i, h.Signal)


def test_generator2():
    @h.paramclass
    class P2:
        f = h.Param(dtype=float, desc="a real number", default=1e-11)

    @h.generator
    def g2(params: P2, ctx: h.Context) -> h.Module:
        # Generator which takes a Context-argument
        assert isinstance(params, P2)
        assert isinstance(ctx, h.Context)
        return h.Module()

    m = h.elaborate(g2(P2()))

    assert isinstance(m, h.Module)
    assert m.name == "g2(f=1e-11)"


def test_generator3():
    @h.paramclass
    class P3:
        width = h.Param(dtype=int, desc="bit-width, maybe", default=1)

    @h.generator
    def g3a(params: P3) -> h.Module:
        return h.Module()

    @h.generator
    def g3b(params: P3, ctx: h.Context) -> h.Module:
        return h.Module()

    M = h.Module(name="M")
    p3a = P3()
    p3b = P3(width=5)

    @h.module
    class HasGen:
        a = g3a(p3a)()
        b = g3b(p3b)()
        c = M()

    # Elaborate the top module
    h.elaborate(HasGen)

    # Post-elab checks
    assert isinstance(HasGen.a, h.Instance)
    assert isinstance(HasGen.a.of, h.GeneratorCall)
    assert HasGen.a.of.gen is g3a
    assert HasGen.a.of.params == P3()
    assert isinstance(HasGen.a.of.result, h.Module)
    assert HasGen.a.of.result.name == "g3a(width=1)"
    assert isinstance(HasGen.b, h.Instance)
    assert isinstance(HasGen.b.of, h.GeneratorCall)
    assert isinstance(HasGen.b.of.result, h.Module)
    assert HasGen.b.of.result.name == "g3b(width=5)"
    assert HasGen.b.of.gen is g3b
    assert HasGen.b.of.params == P3(width=5)
    assert isinstance(HasGen.c, h.Instance)
    assert isinstance(HasGen.c.of, h.Module)
    assert HasGen.c.of is M


def test_array1():
    @h.module
    class InArray:
        inp = h.Input()
        out = h.Output()

    m = h.Module(name="HasArray")
    m.s1 = h.Signal(width=8)
    m.s2 = h.Signal(width=1)
    m.arr = h.InstanceArray(InArray, 8)
    m.arr.inp = m.s1
    m.arr.out = m.s2

    assert m.name == "HasArray"


def test_array2():
    """Basic Instance-Array Test"""
    a = h.Module(name="a")
    a.inp = h.Port(width=1)
    a.out = h.Port(width=1)

    @h.module
    class HasArray2:
        s1 = h.Signal(width=8)
        s2 = h.Signal(width=1)
        arr = h.InstanceArray(a, 8)(inp=s1, out=s2)

    assert len(HasArray2.instances) == 0
    assert len(HasArray2.instarrays) == 1

    # Elaborate, flattening arrays along the way
    h.elaborate(HasArray2)

    # Post-elab checks
    assert len(HasArray2.instances) == 8
    assert len(HasArray2.instarrays) == 0


def test_cycle1():
    """Test cyclical connection-graphs, i.e. a back-to-back pair of instances"""

    @h.module
    class Thing:
        inp = h.Input()
        out = h.Output()

    @h.module
    class BackToBack:
        t1 = Thing()
        t2 = Thing(inp=t1.out, out=t1.inp)

    assert isinstance(BackToBack.t1.inp, h.PortRef)
    assert isinstance(BackToBack.t1.out, h.PortRef)
    assert isinstance(BackToBack.t2.inp, h.PortRef)
    assert isinstance(BackToBack.t2.out, h.PortRef)

    b = h.elaborate(BackToBack)

    assert isinstance(b.t1.inp, h.Signal)
    assert isinstance(b.t1.out, h.Signal)
    assert isinstance(b.t2.inp, h.Signal)
    assert isinstance(b.t2.out, h.Signal)


def test_cycle2():
    """# Doing the same thing in procedural code"""

    @h.module
    class Thing:
        inp = h.Input()
        out = h.Output()

    b2 = h.Module(name="BackToBack2")
    b2.t1 = Thing()
    b2.t2 = Thing()
    b2.t2.inp = b2.t1.out
    b2.t2.out = b2.t1.inp

    assert isinstance(b2.t1.inp, h.PortRef)
    assert isinstance(b2.t1.out, h.PortRef)
    assert isinstance(b2.t2.inp, h.PortRef)
    assert isinstance(b2.t2.out, h.PortRef)

    b2 = h.elaborate(b2)

    assert len(b2.instances) == 2
    assert len(b2.instarrays) == 0
    assert len(b2.bundles) == 0
    assert len(b2.ports) == 0
    assert len(b2.signals) == 2
    assert "t1_out" in b2.signals
    assert "t1_inp" in b2.signals


def test_gen3():
    @h.paramclass
    class MyParams:
        w = h.Param(dtype=int, desc="Input bit-width. Required")

    @h.generator
    def MyThirdGenerator(params: MyParams) -> h.Module:
        @h.module
        class Inner:
            i = h.Input(width=params.w)
            o = h.Output(width=2 * params.w)

        # Instantiate that in another Module
        @h.module
        class Outer:
            i = h.Signal(width=params.w)
            o = h.Signal(width=2 * params.w)
            inner = Inner(i=i, o=o)

        # And manipulate that some more too
        Outer.inp = h.Input(width=params.w)
        return Outer

    h.elaborate(MyThirdGenerator(MyParams(1)))

    # FIXME: post-elab checks


def test_prim1():
    # First test of transistor primitives
    params = h.Mos.Params()
    pmos = h.Pmos(params)
    nmos = h.Nmos(params)

    @h.module
    class HasMos:
        # Two transistors wired in parallel
        p = pmos()
        n = nmos(g=p.g, d=p.d, s=p.s, b=p.b)

    h.elaborate(HasMos)
    # FIXME: post-elab checks


def test_prim2():
    @h.module
    class HasPrims:
        p = h.Signal()
        n = h.Signal()

        _rp = h.R.Params(r=50)
        r = h.Resistor(_rp)(p=p, n=n)

        c = h.Capacitor(h.C.Params(c=1e-12))(p=p, n=n)
        l = h.Inductor(h.L.Params(l=1e-15))(p=p, n=n)
        d = h.Diode(h.D.Params())(p=p, n=n)
        s = h.Short(h.Short.Params())(p=p, n=n)

    h.elaborate(HasPrims)
    # FIXME: post-elab checks


def test_signal_slice1():
    # Initial test of signal slicing

    sig = h.Signal(width=10)
    sl = sig[0]
    assert isinstance(sl, h.Slice)
    assert sl.top == 1
    assert sl.bot == 0
    assert sl.width == 1
    assert sl.step == 1
    assert sl.parent is sig

    sl = sig[0:5]
    assert isinstance(sl, h.Slice)
    assert sl.top == 5
    assert sl.bot == 0
    assert sl.width == 5
    assert sl.step == 1
    assert sl.parent is sig

    sl = sig[:]
    assert isinstance(sl, h.Slice)
    assert sl.top == 10
    assert sl.bot == 0
    assert sl.width == 10
    assert sl.step == 1
    assert sl.parent is sig


def test_signal_slice2():
    # Test slicing advanced features
    sl = h.Signal(width=11)[-1]
    assert sl.top == 11
    assert sl.bot == 10
    assert sl.step == 1
    assert sl.width == 1

    sl = h.Signal(width=11)[:-1]
    assert sl.top == 10
    assert sl.bot == 0
    assert sl.step == 1
    assert sl.width == 10

    sl = h.Signal(width=11)[-2:]
    assert sl.top == 11
    assert sl.bot == 9
    assert sl.step == 1
    assert sl.width == 2


@pytest.mark.xfail(reason="#21 https://github.com/dan-fritchman/Hdl21/issues/21")
def test_bad_slice1():
    # Test slicing error-cases
    with pytest.raises(TypeError):
        h.Signal(width=11)[None]

    with pytest.raises(ValueError):
        h.Signal(width=11)[11]

    h.Signal(width=11)[2:1:-1]  # OK
    with pytest.raises(ValueError):
        h.Signal(width=11)[2:1:1]  # Not OK

    h.Signal(width=11)[1:9]  # OK
    with pytest.raises(ValueError):
        h.Signal(width=11)[9:1]  # Not OK


def test_signal_concat1():
    # Initial Signal concatenation test

    c = h.Concat(h.Signal(width=1), h.Signal(width=2), h.Signal(width=3))
    assert isinstance(c, h.Concat)
    assert len(c.parts) == 3
    for p in c.parts:
        assert isinstance(p, h.Signal)
    assert c.width == 6

    c = h.Concat(h.Signal(width=1)[0], h.Signal(width=2)[0], h.Signal(width=3)[0])
    assert isinstance(c, h.Concat)
    assert len(c.parts) == 3
    for p in c.parts:
        assert isinstance(p, h.Slice)
    assert c.width == 3

    c = h.Concat(
        h.Concat(h.Signal(), h.Signal()), h.Signal(width=2), h.Signal(width=2)[:]
    )
    assert isinstance(c, h.Concat)
    assert len(c.parts) == 3
    assert c.width == 6


def test_slice_module1():
    """Make use of slicing and concatenation in a module"""

    C = h.Module(name="C")
    C.p1 = h.Port(width=1)
    C.p4 = h.Port(width=4)
    C.p7 = h.Port(width=7)

    P = h.Module(name="P")
    P.s4 = h.Signal(width=4)
    P.s2 = h.Signal(width=2)
    P.ic = C(p1=P.s4[0], p4=P.s4, p7=h.Concat(P.s4, P.s2, P.s2[0]))

    h.elaborate(P)


def test_instantiable_as_param():
    """Test using each Instantiable type as a parameter-value."""

    @h.paramclass
    class Params:
        m = h.Param(dtype=h.Module, desc="A `Module`")
        e = h.Param(dtype=h.ExternalModule, desc="An `ExternalModule`")
        ec = h.Param(dtype=h.ExternalModuleCall, desc="An `ExternalModuleCall`")
        # FIXME: `Generator` is the one exception here. Maybe it can work, some day.
        # g = h.Param(dtype=h.Generator, desc="An `Generator`")
        gc = h.Param(dtype=h.GeneratorCall, desc="An `GeneratorCall`")
        p = h.Param(dtype=h.Primitive, desc="An `Primitive`")
        pc = h.Param(dtype=h.PrimitiveCall, desc="An `PrimitiveCall`")
        i = h.Param(dtype=h.Instantiable, desc="An `Instantiable`")

    @h.generator
    def UsesThemParams(params: Params) -> h.Module:
        @h.module
        class M:
            x = h.Signal()

            m = params.m(x=x)
            e = params.e()(x=x)
            ec = params.ec(x=x)
            # g = params.g()(x=x)
            gc = params.gc(x=x)
            p = params.p()(d=x, g=x, s=x, b=x)
            pc = params.pc(d=x, g=x, s=x, b=x)
            i = params.i(x=x)

        return M

    Mod = h.Module(name="Mod")
    Mod.x = h.Port()
    Emod = h.ExternalModule(name="Emod", port_list=[h.Port(name="x")])

    @h.generator
    def Gen(_: h.HasNoParams) -> h.Module:
        m = h.Module()
        m.x = h.Port()
        return m

    p = Params(
        m=Mod,
        e=Emod,
        ec=Emod(),
        # g=Gen,
        gc=Gen(),
        p=h.Mos,
        pc=h.Mos(),
        i=Mod,
    )
    m = UsesThemParams(p)
    m = h.elaborate(m)
    # assert m == Mod


def test_instance_mult():
    """Initial tests of instance-array-generation by multiplication"""

    Child = h.Module(name="Child")
    Parent = h.Module(name="Parent")

    # Create an array via multiplication
    Parent.child = Child() * 5  # Lotta kids here

    # Check that the array is created correctly
    assert isinstance(Parent.child, h.InstanceArray)
    assert Parent.child.n == 5
    assert Parent.child.of is Child

    # Test elaboration
    h.elaborate(Parent)

    # Post-elaboration checks
    assert len(Parent.instances) == 5
    assert len(Parent.instarrays) == 0
    for inst in Parent.instances.values():
        assert inst.of is Child

    # Create another, this time via right-mul
    Parent = h.Module(name="Parent")
    Parent.child = 11 * Child()  # Getting even more kids

    # Check that the array is created correctly
    assert isinstance(Parent.child, h.InstanceArray)
    assert Parent.child.n == 11
    assert Parent.child.of is Child

    # Test elaboration
    h.elaborate(Parent)

    # Post-elaboration checks
    assert len(Parent.instances) == 11
    assert len(Parent.instarrays) == 0
    for inst in Parent.instances.values():
        assert inst.of is Child


def test_instance_mult2():
    """Test connecting to multiplication-generated InstanceArrays"""

    @h.module
    class Child:
        p = h.Port()

    @h.module
    class Parent:
        a = h.Signal(width=3)
        child = (Child() * 3)(p=a)

    assert len(Parent.instances) == 0
    assert len(Parent.instarrays) == 1

    h.elaborate(Parent)

    # Check that array-flattening completed correctly
    assert len(Parent.instances) == 3
    assert len(Parent.instarrays) == 0
    assert Parent.get("child_0").of is Child
    assert Parent.get("child_1").of is Child
    assert Parent.get("child_2").of is Child

    # FIXME: slice equality changes break these tests
    # assert Parent.get("child_0").conns["p"] == Parent.a[0]
    # assert Parent.get("child_1").conns["p"] == Parent.a[1]
    # assert Parent.get("child_2").conns["p"] == Parent.a[2]


def test_instance_mult3():
    """Test connecting to an "already connected" Instance"""

    @h.module
    class Child:
        p = h.Port()

    @h.module
    class Parent:
        a = h.Signal(width=3)
        child = 3 * Child(p=a)  # <= this the one diff here from test_instance_mult2

    h.elaborate(Parent)

    # Check that array-flattening completed correctly
    assert len(Parent.instances) == 3
    assert len(Parent.instarrays) == 0
    assert Parent.get("child_0").of is Child
    assert Parent.get("child_1").of is Child
    assert Parent.get("child_2").of is Child

    # FIXME: slice equality changes break these tests
    # assert Parent.get("child_0").conns["p"] == Parent.a[0]
    # assert Parent.get("child_1").conns["p"] == Parent.a[1]
    # assert Parent.get("child_2").conns["p"] == Parent.a[2]


def test_instance_mult4():
    """Test connecting non-unit-width Arrays"""

    @h.module
    class Child:
        a = h.Port(width=11)
        b = h.Port(width=16)

    @h.module
    class Parent:
        a = h.Signal(width=11)
        b = h.Signal(width=48)
        child = 3 * Child(a=a, b=b)

    h.elaborate(Parent)

    # Check that array-flattening completed correctly
    assert len(Parent.instances) == 3
    assert len(Parent.instarrays) == 0
    assert Parent.get("child_0").of is Child
    assert Parent.get("child_1").of is Child
    assert Parent.get("child_2").of is Child
    assert Parent.get("child_0").conns["a"] == Parent.a
    assert Parent.get("child_1").conns["a"] == Parent.a
    assert Parent.get("child_2").conns["a"] == Parent.a

    # FIXME: we probably want a new Signal/ Slice "equality" method for these
    # assert Parent.get("child_0").conns["b"] == Parent.b[0:16]
    # assert Parent.get("child_1").conns["b"] == Parent.b[16:32]
    # assert Parent.get("child_2").conns["b"] == Parent.b[32:48]


def test_bad_width_conn():
    """Test invalid connection-widths"""
    c = h.Module(name="c")
    c.p = h.Port(width=3)  # Width-3 Port
    q = h.Module(name="q")
    q.s = h.Signal(width=5)  # Width-5 Signal
    q.c = c(p=q.s)  # <= Bad connection here

    with pytest.raises(RuntimeError):
        h.elaborate(q)


def test_illegal_module_attrs():
    """Test attempting to add illegal attributes"""

    m = h.Module()
    with pytest.raises(TypeError):
        m.a = list()

    @h.module
    class M:
        # This version works as of v2.0, since it makes `a`
        # easier to refer to, e.g. as part of an instance parameter.
        a = list()

    @h.module
    class C:
        ...

    with pytest.raises(TypeError):
        C.b = TabError

    # Use combinations of legal attributes

    m = h.Module(name="m")
    with pytest.raises(TypeError):
        m.p = 5
    with pytest.raises(TypeError):
        m.z = dict(a=h.Signal())
    with pytest.raises(TypeError):
        m.q = [h.Port()]
    with pytest.raises(TypeError):
        m.p = (h.Input(), h.Output())
    with pytest.raises(TypeError):
        m.func = lambda _: None

    # As of v2.0 this is allowed, although `fail` does not show up on the resultant `Module`.
    @h.module
    class HasMethod:
        def fail(self):
            ...

    assert not hasattr(HasMethod, "fail")


def test_copy_signal():
    """Copying a Signal"""
    copy.copy(h.Signal())
    copy.deepcopy(h.Signal())


def test_orphanage():
    """Test that orphaned Module-attributes fail at elaboration"""

    m1 = h.Module(name="m1")
    m1.s = h.Signal()  # Signal `s` is now "parented" by `m1`

    m2 = h.Module(name="m2")
    m2.y = m1.s  # Now `s` has been "orphaned" (or perhaps "cradle-robbed") by `m2`

    # Note elaborating `m2` continues to work
    h.elaborate(m2)

    with pytest.raises(RuntimeError):
        # Elaborating `m1` should fail, since `s` is orphaned
        h.elaborate(m1)


def test_orphanage2():
    """Test orphaning a bundle instance"""

    @h.bundle
    class B:
        bb = h.Signal(width=1)

    b = B()  # Instance of `B`-type Bundle, to be orphaned

    m1 = h.Module(name="m1")
    m1.b = b
    m2 = h.Module(name="m2")
    m2.b = b

    # Note elaborating `m2` continues to work
    h.elaborate(m2)

    with pytest.raises(RuntimeError):
        # Elaborating `m1` should fail, since `s` is orphaned
        h.elaborate(m1)


def test_orphanage3():
    """Test orphaning an instance"""
    I = h.Module(name="I")
    i = I()  # Instance to be orphaned

    m1 = h.Module(name="m1")
    m1.i = i
    m2 = h.Module(name="m2")
    m2.i = i

    # Note elaborating `m2` continues to work
    h.elaborate(m2)

    with pytest.raises(RuntimeError):
        # Elaborating `m1` should fail, since `s` is orphaned
        h.elaborate(m1)


def test_orphanage4():
    """Test an orphan Instance connection"""

    m1 = h.Module(name="m1")
    m1.p = h.Port()

    # The "orphan signal" will not be owned by any module
    the_orphan_signal = h.Signal()
    m2 = h.Module(name="m2")
    m2.i = m1(p=the_orphan_signal)  # <= Problem's here

    # Note elaborating `m1` continues to work
    h.elaborate(m1)

    with pytest.raises(RuntimeError):
        # Elaborating `m2` should fail
        h.elaborate(m2)


def test_wrong_decorator():
    """Mistake `Module` for `module` and vice versa"""

    with pytest.raises(TypeError) as e:

        @h.Module  # Bad!
        class M:
            ...

    assert "Did you mean to use the `module` decorator?" in str(e)

    with pytest.raises(TypeError) as e:

        h.Module(2)  # Bad!

    assert "Invalid Module name" in str(e)

    with pytest.raises(TypeError) as e:
        ok = h.Module("ok")  # OK
        h.Module(ok)  # Bad!

    assert "Invalid Module name" in str(e)


def test_elab_noconn():
    """Initial test of elaborating a `NoConn`"""

    @h.module
    class Inner:
        p = h.Port()

    @h.module
    class HasNoConn:
        i1 = Inner()
        i1.p = h.NoConn()

    h.elaborate(HasNoConn)

    assert len(HasNoConn.signals) == 1


def test_elab_noconn2():
    """Slightly more elaborate test of elaborating a `NoConn`"""

    @h.module
    class M3:  # Layer 3: just a Port
        p = h.Port()

    @h.module
    class M2:  # Layer 2: instantiate & connect M3
        p = h.Port()
        m3 = M3(p=p)

    @h.module
    class M1:  # Layer 1: connect a `NoConn` to all that
        p = h.NoConn()
        m2 = M2(p=p)

    h.elaborate(M1)

    assert len(M1.signals) == 1


def test_bad_noconn():
    """Test that a doubly-connected `NoConn` should fail"""

    @h.module
    class Inner:
        p = h.Port()

    @h.module
    class Bad:
        # Create two instances of `Inner`
        i1 = Inner()
        i2 = Inner()

        # Connect the first to a `NoConn`
        i1.p = h.NoConn()
        # And then connect the second to the first.
        # Herein lies the "problem"
        i2.p = i1.p

    with pytest.raises(RuntimeError):
        h.elaborate(Bad)


def test_array_concat_conn():
    """Test connecting a `Concat` to an `InstanceArray`"""

    Child = h.Module(name="Child")
    Child.p3 = h.Input(width=3)
    Child.p5 = h.Input(width=5)

    Parent = h.Module(name="Parent")
    Parent.s5 = h.Signal(width=5)
    Parent.s9 = h.Signal(width=9)
    Parent.c = 2 * Child()
    Parent.c.p3 = Parent.s5[0:3]
    Parent.c.p5 = h.Concat(Parent.s5[3], Parent.s9)


@pytest.mark.xfail(reason="FIXME: structural Slice/ Concat equality ")
def test_slice_resolution():
    """Test resolutions of slice combinations"""

    # This is a very private import of the slice-resolver function
    from hdl21.elab.elaborators.slices import _resolve_slice

    # Slice of a Signal
    s = h.Signal(width=5)
    assert _resolve_slice(s[0]) == s[0]

    # Slice of a Concat
    s1 = h.Signal(name="s1", width=5)
    s2 = h.Signal(name="s2", width=5)
    c = h.Concat(s1, s2)
    assert _resolve_slice(c[0]) == s1[0]
    assert _resolve_slice(c[1]) == s1[1]
    assert _resolve_slice(c[2]) == s1[2]
    assert _resolve_slice(c[3]) == s1[3]
    assert _resolve_slice(c[4]) == s1[4]
    assert _resolve_slice(c[5]) == s2[0]
    assert _resolve_slice(c[6]) == s2[1]
    assert _resolve_slice(c[7]) == s2[2]
    assert _resolve_slice(c[8]) == s2[3]
    assert _resolve_slice(c[9]) == s2[4]

    # Slice of a Slice
    sa = h.Signal(name="sa", width=5)
    assert _resolve_slice(sa[2:5][0]) == sa[2]
    assert _resolve_slice(sa[2:5][1]) == sa[3]
    assert _resolve_slice(sa[2:5][2]) == sa[4]

    assert _resolve_slice(sa[:][0]) == sa[0]
    assert _resolve_slice(sa[:][1]) == sa[1]
    assert _resolve_slice(sa[:][2]) == sa[2]
    assert _resolve_slice(sa[:][3]) == sa[3]
    assert _resolve_slice(sa[:][4]) == sa[4]

    # Check a concatenation case. Note `Concat` does not support equality, so compare parts.
    assert _resolve_slice(sa[:][0:4]).parts == (sa[0], sa[1], sa[2], sa[3])


def test_common_attr_errors():
    """Test that common errors provide helpful feedback.
    For example, adding `Module`s where one wants an `Instance`."""

    M = h.Module(name="M")

    # Module assignment, where we'd want an Instance `M.i = I()`
    I = h.Module(name="I")
    with pytest.raises(TypeError) as einfo:
        M.i = I  # Bad - Module
    assert "Did you mean" in str(einfo.value)
    assert "`Module`" in str(einfo.value)
    M.i = I()  # Good - Instance

    # Primitive assignment
    from hdl21.primitives import R

    with pytest.raises(TypeError) as einfo:
        M.r = R  # Fail - Primitive
    assert "Did you mean" in str(einfo.value)
    assert "`Primitive`" in str(einfo.value)
    with pytest.raises(TypeError) as einfo:
        M.r = R(R.Params(r=1))  # Fail - Primitive Call
    assert "Did you mean" in str(einfo.value)
    assert "`PrimitiveCall`" in str(einfo.value)
    M.r = R(R.Params(r=1))()  # Good - Instances (granted incompletely connected)

    # Generator assignment
    @h.generator
    def G(p: h.HasNoParams) -> h.Module:
        return h.Module()

    with pytest.raises(TypeError) as einfo:
        M.g = G  # Bad - Generator
    assert "Did you mean" in str(einfo.value)
    assert "`Generator`" in str(einfo.value)
    with pytest.raises(TypeError) as einfo:
        M.g = G(h.NoParams)  # Bad - GeneratorCall
    assert "Did you mean" in str(einfo.value)
    assert "`GeneratorCall`" in str(einfo.value)
    M.g = G(h.NoParams)()  # Good - Instance

    X = h.ExternalModule(name="X", port_list=[])
    with pytest.raises(TypeError) as einfo:
        M.x = X  # Bad - ExternalModule
    assert "Did you mean" in str(einfo.value)
    assert "`ExternalModule`" in str(einfo.value)
    with pytest.raises(TypeError) as einfo:
        M.x = X()  # Bad - ExternalModuleCall
    assert "Did you mean" in str(einfo.value)
    assert "`ExternalModuleCall`" in str(einfo.value)
    M.x = X()()  # Good - Instance


def test_generator_call_by_kwargs():
    """Test the capacity for generators to create their param-classes inline."""

    @h.paramclass
    class P:
        a = h.Param(dtype=int, desc="a")
        b = h.Param(dtype=float, desc="b")
        c = h.Param(dtype=str, desc="c")

    @h.generator
    def M(_: P) -> h.Module:
        return h.Module()

    # Call without constructing a `P`
    m = M(a=1, b=2.0, c="3")

    assert isinstance(m, h.GeneratorCall)
    m = h.elaborate(m)
    assert isinstance(m, h.Module)

    # Check that type-checking continue
    with pytest.raises(RuntimeError):
        m = M(a=TabError, b=TabError, c=TabError)


def test_instance_array_portrefs():
    """Test Instance Arrays connected by port-references"""

    Inv = h.ExternalModule(
        name="Inv",
        port_list=[
            h.Input(name="i"),
            h.Output(name="z"),
        ],
    )

    m = h.Module(name="TestArrayPortRef")
    m.a, m.b = h.Signals(2, width=4)

    # Create an InstanceArray
    m.inva = 4 * Inv()(i=m.a)
    # And another which connects to it via PortRef
    m.invb = 4 * Inv()(i=m.inva.z, z=m.b)

    h.elaborate(m)

    assert len(m.instances) == 8
    assert len(m.instarrays) == 0


def test_array_bundle():
    """Test bundle-valued connections to instance arrays."""

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class HasB:
        b = B(port=True)

    @h.module
    class HasArr:
        b = B()
        bs = 11 * HasB(b=b)

    # Elaborate this,
    h.elaborate(HasArr)

    assert len(HasArr.signals) == 1
    assert len(HasArr.instances) == 11
    assert len(HasArr.instarrays) == 0
    for inst in HasArr.instances.values():
        assert inst.conns.get("b_s", None) is HasArr.b_s


def test_multiple_signals_in_port_group():
    """Test, or at least try to test, jamming more than one Signal
    into the `group` concept used by the `ResolvePortRefs` elaborator pass.
    Based on the design of `ResolvePortRefs`, this is a thing that (we think)
    is not possible."""

    @h.module
    class I:
        s = h.Port()

    @h.module
    class M:
        s = h.Signal()
        i1 = I(s=s)
        i2 = I(s=s)
        i3 = I(s=i1.s)
        i4 = I(s=i2.s)

    h.elaborate(M)

    # Check this resolved to a single Signal
    assert len(M.signals) == 1
    assert len(M.bundles) == 0
    assert len(M.instances) == 4

    # And check that Signal is connected to all four Instances
    assert M.i1.s is M.s
    assert M.i2.s is M.s
    assert M.i3.s is M.s
    assert M.i4.s is M.s


def test_bad_conns():
    """Test the errors produced by elaborating with invalid Port connections"""

    @h.module
    class I:
        p = h.Port()

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a, b=b, p=c)  # Two of these 3 ports don't exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Connection to non-existent Port" in str(e.value)

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a, b=b)  # None of these ports exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Missing connection to" in str(e.value)
    assert "Connection to non-existent Port" in str(e.value)

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a, p=b)  # One of these ports don't exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Connection to non-existent Port" in str(e.value)

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a)  # All (one) port doesn't exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Missing connection to" in str(e.value)


def test_generator_port_slice():
    """Test taking a slice from a Generator `PortRef`."""

    @h.paramclass
    class Width:
        width = h.Param(dtype=int, desc="Width")

    @h.generator
    def SliceMyP(params: Width) -> h.Module:
        m = h.Module()
        m.p = h.Port(width=params.width)  # Port with parametrized width
        return m

    @h.module
    class ScalarPort:
        p = h.Port()  # A width-one port

    @h.module
    class HasGen:
        g = SliceMyP(width=8)()
        # Connect the MSB of `g.p` to `s.p`
        s = ScalarPort(p=g.p[-1])

    h.elaborate(HasGen)


def test_pair1():
    """Test of the `Diff` and `Pair` signal and instance bundles"""

    @h.module
    class I:
        ps = h.Port(desc="Port we'll connect to a scalar")
        pd = h.Port(desc="Port we'll connect to a diff")
        pa = h.Port(desc="Port we'll connect to an AnonymousBundle")

    @h.module
    class O:
        d = h.Diff()
        s = h.Signal()
        pair = h.Pair(I)(pd=d, ps=s, pa=h.inverse(d))

    h.elaborate(O)

    assert len(O.instances) == 2
    assert "pair_p" in O.instances
    assert "pair_n" in O.instances
    assert O.pair_p.conns["ps"] is O.s
    assert O.pair_n.conns["ps"] is O.s
    assert O.pair_p.conns["pd"] is O.d_p
    assert O.pair_n.conns["pd"] is O.d_n
    assert O.pair_p.conns["pa"] is O.d_n
    assert O.pair_n.conns["pa"] is O.d_p
    assert len(O.signals) == 3
    assert len(O.bundles) == 0
    assert len(O.instbundles) == 0


def test_noconn_types():
    """Test connecting `NoConn`s to a variety of port-types."""

    @h.module
    class Inner:
        # Inner module with a handful of port-types
        s = h.Port()
        b = h.Port(width=11)
        d = h.Diff(port=True)

    @h.module
    class Outer:
        i = Inner(s=h.NoConn(), b=h.NoConn(), d=h.NoConn())

    # Most of the test is here, just seeing that this can elaborate
    h.elaborate(Outer)

    assert len(Inner.signals) == 0
    assert len(Outer.ports) == 0
    assert sorted(Inner.ports.keys()) == ["b", "d_n", "d_p", "s"]
    assert sorted(Outer.signals.keys()) == ["i_b", "i_d_n", "i_d_p", "i_s"]
    assert Outer.i.conns["b"] is Outer.i_b
    assert Outer.i.conns["d_n"] is Outer.i_d_n
    assert Outer.i.conns["d_p"] is Outer.i_d_p
    assert Outer.i.conns["s"] is Outer.i_s


def test_deep_hierarchy():
    """Test a deep hierarchy, without much content."""

    # Create the leaf level module. Empty with a single Port `p`.
    M0 = h.Module(name=f"M0")
    M0.p = h.Port()
    prev = M0
    M1 = None

    # Create lots of layers above it, each of which instantiates the previous.
    for k in range(100):
        m = h.Module(name=f"M{k}")
        m.p = h.Port()
        m.i = h.Instance(of=prev)(p=m.p)
        if M1 is None:
            M1 = m
        prev = m

    # Screw up a connection, and check that we get an elaboration-time error when elaborating the top-level module.
    M1.i.not_a_real_port = M1.p
    with pytest.raises(RuntimeError):
        h.elaborate(m)


def test_generator_eq():
    """Test equality and hashing of Generator calls using `Default`."""

    @h.paramclass
    class Params:
        p = h.Param(dtype=int, desc="p", default=111)

    @h.generator
    def Gen(_: Params) -> h.Module:
        return h.Module()

    assert Gen() == Gen()
    assert Gen() == Gen(Params(p=111))
    assert Gen() == Gen(p=111)
    assert Gen().params == Params()
    assert Gen().params == Params(p=111)

    assert hash(Gen()) == hash(Gen(Params(p=111)))
    assert hash(Gen()) == hash(Gen(p=111))


def test_param_calls():
    """ " Test creation of `Primitive`s and `ExternalModule` calls with inline construction of their parameters."""

    Ext = h.ExternalModule(name="Ext", port_list=[], paramtype=dict)
    call = Ext(a=1, b="c", d=TabError)
    assert isinstance(call, h.ExternalModuleCall)
    assert call.params == dict(a=1, b="c", d=TabError)

    with pytest.raises(TypeError):
        Ext("not_a_dict_as_positional_arg")
    with pytest.raises(RuntimeError):
        Ext(dict(), b="d")

    @h.paramclass
    class P:
        reqd = h.Param(dtype=float, desc="reqd")
        a = h.Param(dtype=int, desc="a", default=111)
        b = h.Param(dtype=str, desc="b", default="c")

    Ext = h.ExternalModule(name="Ext", port_list=[], paramtype=P)
    call = Ext(reqd=3.14159, a=1, b="q")
    assert isinstance(call, h.ExternalModuleCall)
    assert call.params == P(reqd=3.14159, a=1, b="q")

    with pytest.raises(TypeError):
        Ext("not_a_P_as_positional_arg")
    with pytest.raises(RuntimeError):
        Ext(P(reqd=3.14159), a=12)

    from hdl21.primitives import R, ResistorParams

    call = R(r=11)
    assert isinstance(call, h.PrimitiveCall)
    assert call == R(R.Params(r=11))
    assert call == R(ResistorParams(r=11))

    with pytest.raises(TypeError):
        R("not_a_ResistorParams_as_positional_arg")
    with pytest.raises(RuntimeError):
        R(R.Params(r=11), z=12)


def test_bad_generators():
    """Test generator functions with bad call-signatures."""

    @h.paramclass
    class P:
        ...

    @h.generator  # A good, working generator!
    def good(p: P) -> h.Module:
        return h.Module()

    with pytest.raises(RuntimeError):
        # Bad 1st argument type
        @h.generator
        def bad(p: TabError) -> h.Module:
            return h.Module()

    with pytest.raises(RuntimeError):
        # Bad 2nd argument type
        @h.generator
        def bad(p: P, ctx: TabError) -> h.Module:
            return h.Module()

    with pytest.raises(RuntimeError):
        # Extra arg
        @h.generator
        def bad(p: P, ctx: h.Context, something_else: int) -> h.Module:
            return h.Module()

    with pytest.raises(RuntimeError):
        # Bad return type
        @h.generator
        def bad(p: P) -> TabError:
            return h.Module()


def test_multi_portref_conns():
    """Test making several PortRef-based connections with a single assignment line."""

    @h.module
    class I:  # Inner Module
        a, b = h.Ports(2)

    @h.module
    class O:  # Outer, instantiating Module
        i1 = I()
        i2 = I()
        i3 = I()

        # The several connections
        i1.a = i2.a = i3.a

    # And do so again outside the class body
    O.i1.b = O.i2.b = O.i3.b

    h.elaborate(O)

    assert list(O.signals.keys()) == ["i3_a", "i3_b"]
    assert O.i1.conns["a"] is O.i2.conns["a"] is O.i3.conns["a"] is O.i3_a
    assert O.i1.conns["b"] is O.i2.conns["b"] is O.i3.conns["b"] is O.i3_b
