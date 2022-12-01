"""
# Logical Encoder Example 

A demonstration of: 
* Using `ExternalModule`s of externally-defined logic cells 
* Creating a *recursive* `Module` generator, for a parameteric-width one-hot encoder
"""

import sys
import hdl21 as h

"""
## Generic Logic Cells
In a more fully featured use-case, these would map to a target library. 
"""

Inv = h.ExternalModule(
    name="Inv",
    port_list=[
        h.Input(name="i"),
        h.Output(name="z"),
    ],
    desc="Generic Inverter",
)
And2 = h.ExternalModule(
    name="And2",
    port_list=[
        h.Input(name="a"),
        h.Input(name="b"),
        h.Output(name="z"),
    ],
    desc="Generic 3-Input And Gate",
)
And3 = h.ExternalModule(
    name="And3",
    port_list=[
        h.Input(name="a"),
        h.Input(name="b"),
        h.Input(name="c"),
        h.Output(name="z"),
    ],
    desc="Generic 3-Input And Gate",
)
TriInv = h.ExternalModule(
    name="TriInv",
    port_list=[
        h.Input(name="i"),
        h.Input(name="en"),
        h.Output(name="z"),
    ],
    desc="Generic Tri-State Inverter",
)
Flop = h.ExternalModule(
    name="Flop",
    port_list=[
        h.Input(name="d"),
        h.Input(name="clk"),
        h.Output(name="q"),
    ],
    desc="Generic Rising-Edge D Flip Flop",
)
FlopResetLow = h.ExternalModule(
    name="FlopResetLow",
    port_list=[
        h.Input(name="d"),
        h.Input(name="clk"),
        h.Input(name="rstn"),
        h.Output(name="q"),
    ],
    desc="Rising-Edge D Flip Flop. Output low with reset asserted.",
)
FlopResetHigh = h.ExternalModule(
    name="FlopResetHigh",
    port_list=[
        h.Input(name="d"),
        h.Input(name="clk"),
        h.Input(name="rstn"),
        h.Output(name="q"),
    ],
    desc="Rising-Edge D Flip Flop. Output high with reset asserted.",
)
Latch = h.ExternalModule(
    name="Latch",
    port_list=[
        h.Input(name="d"),
        h.Input(name="clk"),
        h.Output(name="q"),
    ],
    desc="Generic Active High Level-Sensitive Latch",
)


@h.paramclass
class Width:
    """Parameter class for Generators with a single integer-valued `width` parameter."""

    width = h.Param(dtype=int, desc="Parametric Width", default=1)


@h.module
class OneHotEncoder2to4:
    """
    # One-Hot Encoder
    2b to 4b with enable.
    Also serves as the base-case for the recursive `OneHotEncoder` generator.
    All outputs are low if enable-input `en` is low.
    """

    # IO Interface
    en = h.Input(width=1, desc="Enable input. Active high.")
    bin = h.Input(width=2, desc="Binary valued input")
    th = h.Output(width=4, desc="Thermometer encoded output")

    # Internal Contents
    # Input inverters
    binb = h.Signal(width=2, desc="Inverted binary input")
    invs = 2 * Inv()(i=bin, z=binb)

    # The primary logic: a set of four And3's
    ands = 4 * And3()(
        a=h.Concat(binb[0], bin[0], binb[0], bin[0]),
        b=h.Concat(binb[1], binb[1], bin[1], bin[1]),
        c=en,
        z=th,
    )


@h.generator
def OneHotEncoder(p: Width) -> h.Module:
    """
    # One-Hot Encoder Generator

    Recursively creates a `p.width`-bit one-hot encoder Module comprised of `OneHotEncoder2to4`s.
    Also generates `OneHotEncoder` Modules for `p.width-2`, `p.width-4`, et al, down to
    the base case two to four bit Module.
    """

    if p.width < 2:
        raise ValueError(f"OneHotEncoder {p} width must be > 1")
    if p.width % 2:
        raise ValueError(f"OneHotEncoder {p} width must be even")
    if p.width == 2:  # Base case: the 2 to 4b encoder
        return OneHotEncoder2to4

    # Recursive case.
    m = h.Module()
    m.en = h.Input(width=1, desc="Enable input. Active high.")
    m.bin = h.Input(width=p.width, desc="Binary valued input")
    m.th = h.Output(width=2**p.width, desc="Thermometer encoded output")

    # Thermo-encode the two MSBs, creating select signals for the LSBs
    m.lsb_sel = h.Signal(width=4)
    m.msb_encoder = OneHotEncoder2to4(en=m.en, bin=m.bin[-2:], th=m.lsb_sel)

    # Peel off two bits and recursively generate our child encoder Module
    child = OneHotEncoder(width=p.width - 2)
    # And create four instances of it, enabled by the thermo-decoded MSBs
    m.children = 4 * child(en=m.lsb_sel, bin=m.bin[:-2], th=m.th)

    return m


def main():
    # "Main" Script Action
    h.netlist(h.to_proto(OneHotEncoder(width=10)), dest=sys.stdout)
    h.netlist(h.to_proto(OneHotEncoder(width=8)), dest=sys.stdout)


if __name__ == "__main__":
    main()
