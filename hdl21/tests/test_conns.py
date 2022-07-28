import hdl21 as h


def test_resolve_portref_type():
    """ Test resolution of PortRef "types" to their Module-level referents """
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
    """ Test concatenating Port References """

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
    """ Test slicing Port References """

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
    """ Test resolution of BundleRef "types" to their Bundle-level referents """
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
    """ Test concatenating Bundle References """

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
    """ Test slicing Bundle References """

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

