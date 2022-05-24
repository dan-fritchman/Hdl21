""" 
Phase Interpolator Example 
"""

from enum import Enum, auto
from io import StringIO
import hdl21 as h
from hdl21.primitives import Nmos, Pmos, MosParams


@h.paramclass
class PhaseWeighterParams:
    wta = h.Param(dtype=int, desc="Weight of Input A")
    wtb = h.Param(dtype=int, desc="Weight of Input B")


@h.generator
def PhaseWeighter(p: PhaseWeighterParams) -> h.Module:
    """ Phase-weighting inverter-pair 
    Drives a single output with two out-of-phase inputs `a` and `b`, 
    with weights dictates by params `wta` and `wtb`. """

    @h.module
    class PhaseWeighter:
        # IO Ports
        a, b = h.Inputs(2)
        out = h.Output()
        mix = h.Signal(desc="Internal phase-mixing node")

        # a-input inverter
        pa = Pmos(MosParams(npar=p.wta))(d=mix, g=a)
        na = Nmos(MosParams(npar=p.wta))(d=mix, g=a)
        # b-input inverter
        pb = Pmos(MosParams(npar=p.wtb))(d=mix, g=b)
        nb = Nmos(MosParams(npar=p.wtb))(d=mix, g=b)
        # Output inverter, with the combined size of the two inputs
        po = Pmos(MosParams(npar=p.wta + p.wtb))(d=out, g=mix)
        no = Nmos(MosParams(npar=p.wta + p.wtb))(d=out, g=mix)

    return PhaseWeighter


@h.bundle
class QuadClock:
    """ # Quadrature Clock Bundle 
    Includes four 90-degree-separated phases. """

    class Roles(Enum):
        # Clock roles: source or sink
        SOURCE = auto()
        SINK = auto()

    ck0 = h.Signal()
    ck90 = h.Signal()
    ck180 = h.Signal()
    ck270 = h.Signal()


@h.paramclass
class PiParams:
    """ Phase Interpolator Parameters """

    nbits = h.Param(dtype=int, default=5, desc="Resolution, or width of select-input.")


@h.generator
def PhaseGenerator(p: PiParams) -> h.Module:
    """ Phase Generator """
    PhaseGen = h.Module()
    ckq = PhaseGen.ckq = QuadClock(
        role=QuadClock.Roles.SINK, port=True
    )  ##, desc="Quadrature input")
    phases = PhaseGen.phases = h.Output(
        width=2 ** p.nbits, desc="Array of equally-spaced phases"
    )

    if p.nbits != 5:
        raise ValueError(
            f"Yeah we know that's a parameter, but this is actually hard-coded to 5 bits for now"
        )

    # Generate a set of PhaseWeighters and output phases for each pair of quadrature inputs
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck0, b=ckq.ck90, out=phases[index]),
        )
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = 8 + wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck90, b=ckq.ck180, out=phases[index]),
        )
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = 16 + wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck180, b=ckq.ck270, out=phases[index]),
        )
    for wtb in range(8):
        p = PhaseWeighterParams(wta=7 - wtb, wtb=wtb)
        index = 24 + wtb
        PhaseGen.add(
            name=f"weight{index}",
            val=PhaseWeighter(p)(a=ckq.ck270, b=ckq.ck0, out=phases[index]),
        )

    return PhaseGen


@h.generator
def PhaseSelector(p: PiParams) -> h.Module:
    @h.module
    class PhaseSelector:
        phases = h.Input(width=2 ** p.nbits, desc="Array of equally-spaced phases")
        sel = h.Input(width=p.nbits, desc="Selection input")
        out = h.Output(width=1, desc="Clock output")
        # COMING SOON! the actual content

    return PhaseSelector


@h.generator
def PhaseInterp(p: PiParams) -> h.Module:
    """ Phase Interpolator Generator """

    @h.module
    class PhaseInterp:
        # IO Interface
        ckq = QuadClock(role=QuadClock.Roles.SINK, port=True, desc="Quadrature input")
        sel = h.Input(width=p.nbits, desc="Selection input")
        out = h.Output(width=1, desc="Clock output")

        # Internal Signals
        phases = h.Signal(width=2 ** p.nbits, desc="Array of equally-spaced phases")

        # Instantiate the phase-generator and phase-selector
        phgen = PhaseGenerator(p)(ckq=ckq, phases=phases)
        phsel = PhaseSelector(p)(phases=phases, sel=sel, out=out)

    return PhaseInterp


# Run the default version
s = StringIO()
h.netlist(h.to_proto(PhaseInterp()), dest=s)
print(s.getvalue())
