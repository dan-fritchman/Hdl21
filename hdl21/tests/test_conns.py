import hdl21 as h


def test_resolve_portref_type():
    """Test resolution of PortRef "types" to their Module-level referents"""
    from hdl21.elab.elaborators.resolve_ref_types import resolve_portref_type

    @h.module
    class Inner:
        p = h.Port()

    @h.module
    class Outer:
        i = Inner()

    # Create a `PortRef`
    ref = Outer.i.p

    # All of these succeed:
    assert ref is Outer.i.p
    assert resolve_portref_type(ref) is not Outer.i.p
    assert resolve_portref_type(ref) is Inner.p


def test_portref_concat():
    """Test concatenating Port References"""

    @h.module
    class A:
        p = h.Port(width=1)

    @h.module
    class B:
        p = h.Port(width=3)

    @h.module
    class Outer:
        a = A()
        b = B(p=h.Concat(a.p, a.p, a.p))

    h.elaborate(Outer)


def test_portref_slice():
    """Test slicing Port References"""

    @h.module
    class A:
        p = h.Port(width=1)

    @h.module
    class B:
        p = h.Port(width=3)

    @h.module
    class Outer:
        b = B()
        a = A(p=b.p[2])

    h.elaborate(Outer)


def test_resolve_bundleref_type():
    """Test resolution of BundleRef "types" to their Bundle-level referents"""
    from hdl21.elab.elaborators.resolve_ref_types import resolve_bundleref_type

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class Outer:
        b = B()

    # Create a `BundleRef`
    ref = Outer.b.s

    # All of these succeed:
    assert ref is Outer.b.s
    assert resolve_bundleref_type(ref) is not Outer.b.s
    assert resolve_bundleref_type(ref) is B.s


def test_bundleref_concat():
    """Test concatenating Bundle References"""

    @h.module
    class Inner:
        p = h.Port(width=3)

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class Outer:
        b = B()
        i = Inner(p=h.Concat(b.s, b.s, b.s))

    h.elaborate(Outer)


def test_bundleref_slice():
    """Test slicing Bundle References"""

    @h.module
    class Inner:
        p = h.Port(width=2)

    @h.bundle
    class B:
        s = h.Signal(width=8)

    @h.module
    class Outer:
        b = B()
        i = Inner(p=b.s[1:3])

    h.elaborate(Outer)


def test_anon_with_signal():
    """Test an AnonymousBundle with a Signal"""

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        s = h.Signal()
        i = Inner(b=h.AnonymousBundle(s=s))

    h.elaborate(Outer)


def test_anon_with_concat():
    """Test an AnonymousBundle with a concatenation"""

    @h.bundle
    class B:
        s = h.Signal(width=2)

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        s = h.Signal(width=1)
        i = Inner(b=h.AnonymousBundle(s=h.Concat(s, s)))

    h.elaborate(Outer)


def test_anon_with_slice():
    """Test an AnonymousBundle with a slice"""

    @h.bundle
    class B:
        s = h.Signal(width=2)

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        s = h.Signal(width=4)
        i = Inner(b=h.AnonymousBundle(s=s[0:2]))

    h.elaborate(Outer)


def test_anon_with_bundle_inst():
    """Test an AnonymousBundle referring to a BundleInstance"""

    @h.bundle
    class BI:
        x = h.Signal()

    @h.bundle
    class B:
        y = h.Signal()
        bi = BI()

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        z = h.Signal()
        bi = BI()
        i = Inner(b=h.AnonymousBundle(y=z, bi=bi))

    h.elaborate(Outer)


def test_anon_with_bundleref_signal():
    """Test an AnonymousBundle referring to a sub-bundle reference"""

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        b = B()
        i = Inner(b=h.AnonymousBundle(s=b.s))

    h.elaborate(Outer)

    assert len(Outer.signals) == 1
    assert len(Outer.ports) == 0
    assert len(Outer.bundles) == 0
    assert len(Inner.signals) == 0
    assert len(Inner.ports) == 1
    assert len(Inner.bundles) == 0
    assert Inner.ports["b_s"]
    assert Outer.i.conns["b_s"] is Outer.signals["b_s"]


def test_anon_with_subbundle_ref():
    """Test an AnonymousBundle referring to a sub-bundle reference"""

    @h.bundle
    class BI:
        x = h.Signal()

    @h.bundle
    class B:
        y = h.Signal()
        bi = BI()

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        z = h.Signal()
        b = B()
        i = Inner(b=h.AnonymousBundle(y=z, bi=b.bi))

    h.elaborate(Outer)


def test_anon_with_portref():
    """Test an AnonymousBundle referring to a PortRef"""

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class HasBPort:
        b = B(port=True)

    @h.module
    class HasSignalPort:
        s = h.Port()

    @h.module
    class Outer:
        hass = HasSignalPort()
        hasb = HasBPort(b=h.AnonymousBundle(s=hass.s))

    h.elaborate(Outer)


def test_anon_with_anon():
    """Test an AnonymousBundle with a nested AnonymousBundle"""

    @h.bundle
    class BI:
        x = h.Signal()

    @h.bundle
    class B:
        y = h.Signal()
        bi = BI()

    @h.module
    class Inner:
        b = B(port=True)

    @h.module
    class Outer:
        a, b = h.Signals(2)
        i = Inner(b=h.AnonymousBundle(y=a, bi=h.AnonymousBundle(x=b)))

    h.elaborate(Outer)
