"""
# Hdl21 Unit Tests
Pulling directly from the documenation snippets, and making sure they work as claimed. 
"""

import hdl21 as _h


@_h.module
class AnotherModule:
    # This module is not defined in the docs, but of course is needed to actually run.
    a, b, c = _h.Ports(3)


def test_module1():
    import hdl21 as h

    m = h.Module(name="MyModule")
    m.i = h.Input()
    m.o = h.Output(width=8)
    m.s = h.Signal()
    m.a = AnotherModule()


def test_module2():
    import hdl21 as h

    @h.module
    class MyModule:
        i = h.Input()
        o = h.Output(width=8)
        s = h.Signal()
        a = AnotherModule()


def test_module3():
    import hdl21 as h

    @h.module
    class MyModule:
        a, b = h.Inputs(2)
        c, d, e = h.Outputs(3, width=16)
        z, y, x, w = h.Signals(4)


def test_module4():
    import hdl21 as h

    # Create a module
    m = h.Module()
    # Create its internal Signals
    m.a, m.b, m.c = h.Signals(3)
    # Create an Instance
    m.i1 = AnotherModule()
    # And wire them up
    m.i1.a = m.a
    m.i1.b = m.b
    m.i1.c = m.c


def test_module4():
    import hdl21 as h

    # Create a module
    m = h.Module()
    # Create the Instances
    m.i1 = AnotherModule()
    m.i2 = AnotherModule()
    # Call one to connect them
    m.i1(a=m.i2.a, b=m.i2.b, c=m.i2.c)


def test_module5():
    import hdl21 as h

    # Create a module
    m = h.Module()
    # Create the Instance `i1`
    m.i1 = AnotherModule()
    # Create another Instance `i2`, and connect to `i1`
    m.i2 = AnotherModule(a=m.i1.a, b=m.i1.b, c=m.i1.c)


@_h.paramclass
class MyParams:
    # Reused by the generator tests to follow
    w = _h.Param(dtype=int, default=8, desc="Width")


def test_generator1():
    import hdl21 as h

    @h.generator
    def MyFirstGenerator(params: MyParams) -> h.Module:
        # A very exciting first generator function
        m = h.Module()
        m.i = h.Input(width=params.w)
        return m

    call = MyFirstGenerator(MyParams(w=16))
    assert isinstance(call, h.GeneratorCall)
    assert call.params == MyParams(w=16)


def test_generator2():
    import hdl21 as h

    @h.generator
    def MySecondGenerator(params: MyParams) -> h.Module:
        # A very exciting (second) generator function
        @h.module
        class MySecondGen:
            i = h.Input(width=params.w)

        return MySecondGen

    # FIXME: checks


def test_generator3():
    import hdl21 as h

    @h.generator
    def MyThirdGenerator(params: MyParams) -> h.Module:
        # Create an internal Module
        @h.module
        class Inner:
            i = h.Input(width=params.w)

        # Manipulate it a bit
        Inner.o = h.Output(width=2 * Inner.i.width)

        # Instantiate that in another Module
        @h.module
        class Outer:
            inner = Inner()

        # And manipulate that some more too
        Outer.inp = h.Input(width=params.w)
        return Outer

    # FIXME: checks


def test_params1():
    import hdl21 as h

    @h.paramclass
    class MyParams:
        # Required
        width = h.Param(dtype=int, desc="Width. Required")
        # Optional - including a default value
        text = h.Param(dtype=str, desc="Optional string", default="My Favorite Module")

    p = MyParams(width=8, text="Your Favorite Module")
    assert p.width == 8  # Passes. Note this is an `int`, not a `Param`
    assert p.text == "Your Favorite Module"  # Also passes


def test_params2():
    import hdl21 as h
    from dataclasses import asdict

    @h.paramclass
    class Inner:
        i = h.Param(dtype=int, desc="Inner int-field")

    @h.paramclass
    class Outer:
        inner = h.Param(dtype=Inner, desc="Inner fields")
        f = h.Param(dtype=float, desc="A float", default=3.14159)

    # Create from a (nested) dictionary literal
    d1 = {"inner": {"i": 11}, "f": 22.2}
    o = Outer(**d1)
    # Convert back to another dictionary
    d2 = asdict(o)
    # And check they line up
    assert d1 == d2


def test_external_module_primitive_example():
    """Test for the Primitives and ExternalModules example"""

    import hdl21 as h
    from hdl21.prefix import µ
    from hdl21.primitives import Diode

    @h.paramclass
    class BandGapParams:
        self_destruct = h.Param(
            dtype=bool,
            desc="Whether to include the self-destruction feature",
            default=True,
        )

    BandGap = h.ExternalModule(
        name="BandGap",
        desc="Example ExternalModule, defined outside Hdl21",
        port_list=[h.Port(name="vref"), h.Port(name="enable")],
        paramtype=BandGapParams,
    )

    params = BandGapParams(self_destruct=False)  # Watch out there!

    @h.module
    class BandGapPlus:
        vref, enable = h.Signals(2)
        # Instantiate the `ExternalModule` defined above
        bg = BandGap(params)(vref=vref, enable=enable)
        # ...Anything else...

    @h.module
    class DiodePlus:
        p, n = h.Signals(2)
        # Parameterize, instantiate, and connect a `primitives.Diode`
        d = Diode(w=1 * µ, l=1 * µ)(p=p, n=n)
        # ... Everything else ...

    """ 
    The part outside the docs: testing it 
    """

    assert isinstance(BandGapPlus, h.Module)
    assert isinstance(BandGapPlus.bg, h.Instance)
    assert isinstance(BandGapPlus.bg.of, h.ExternalModuleCall)
    assert isinstance(DiodePlus, h.Module)
    assert isinstance(DiodePlus.d, h.Instance)
    assert isinstance(DiodePlus.d.of, h.PrimitiveCall)
