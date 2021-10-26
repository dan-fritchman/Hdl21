import sys

import hdl21 as h
from hdl21.diff import Diff


@h.paramclass
class AmpParams:
    nmos = h.Param(dtype=h.Instantiable, desc="Nmos Module")
    pmos = h.Param(dtype=h.Instantiable, desc="Pmos Module")


@h.generator
def FoldedCascode(params: AmpParams) -> h.Module:
    """ Folded Cascode Op-Amp """

    nmos, pmos = params.nmos, params.pmos

    @h.module
    class FoldedCascode:
        # Declare I/O
        inp = Diff(port=True)
        out = h.Output()
        VDD, VSS, ibias = h.Inputs(3)
        # Internal Signals
        outm, s1, s2, g1 = h.Signals(4)

        # Bias Mirrors. Traditional cascode (for now).
        # NMOS Gate Bias
        nbias = Stack(
            ncasc=nmos(g=ibias, d=ibias),  # Top Cascode Diode
            nsrc=nmos(g=s1, d=s1),  # Bottom Bias Diode
        )
        # PMOS Gate Bias
        pbias = Stack(
            psrc=pmos(g=s2, d=s2),  # PMOS Source
            pcasc=pmos(g=g1, d=g1),  # PMOS Cascode
            ncasc=nmos(g=nbias.ncasc.g),
            nsrc=nmos(g=nbias.nsrc.g),
        )
        # Cascode Stack
        ostack = Diffn(
            Stack(
                psrc=2 * pmos(g=pbias.psrc.g),  # PMOS Source
                pcasc=pmos(g=pbias.pcasc.g, d=h.AnonymousBundle(p=out, n=outm)),
                ncasc=nmos(g=nbias.ncasc.g, d=h.AnonymousBundle(p=out, n=outm)),
                nsrc=nmos(g=outm),  # NMOS Mirror
            )
        )
        # Input Stack
        istack = Stack(
            # Differential Input Pair
            nin=Diffn(nmos(g=inp, d=ostack.psrc.d)),
            # Cascoded Bias
            ncasc=2 * nmos(g=nbias.ncasc.g),  # NMOS Cascode
            nsrc=2 * nmos(g=nbias.nsrc.g),  # NMOS Source
        )
        # Matching Constraints (in addition to differential-ness)
        Matched(nbias.ncasc, pbias.ncasc, ostack.ncasc, istack.ncasc)
        Matched(nbias.nsrc, pbias.nsrc, ostack.nsrc, istack.nsrc)

    return FoldedCascode


@h.generator
def FiveXtorAmp(params: AmpParams) -> h.Module:
    """ "Five-Transistor" Op-Amp """

    nmos, pmos = params.nmos, params.pmos

    @h.module
    class Amp:
        # First declare our I/O
        inp = Diff(port=True)
        out = Diff(port=True)
        VDD, VSS, ibias, vbias = h.Inputs(4)

        # Bias mirror
        ndiode = nmos(g=ibias, d=ibias, s=VSS, b=VSS)
        nibias = nmos(g=ibias, s=VSS, b=VSS)
        # Input pair
        ninp = nmos(g=inp.p, d=out.n, s=nibias.d, b=VSS)
        ninn = nmos(g=inp.n, d=out.p, s=nibias.d, b=VSS)
        # Output load
        pldp = pmos(g=vbias, d=out.p, s=VDD, b=VDD)
        pldm = pmos(g=vbias, d=out.n, s=VDD, b=VDD)

    return Amp


PdkNmos = h.ExternalModule(
    name="PdkNmos",
    desc="PDK NMOS Transistor",
    port_list=[
        h.Inout(name="d"),
        h.Inout(name="g"),
        h.Inout(name="s"),
        h.Inout(name="b"),
    ],
    paramtype=h.HasNoParams,
)
PdkPmos = h.ExternalModule(
    name="PdkPmos",
    desc="PDK PMOS Transistor",
    port_list=[
        h.Inout(name="d"),
        h.Inout(name="g"),
        h.Inout(name="s"),
        h.Inout(name="b"),
    ],
    paramtype=h.HasNoParams,
)


def Matched(*args, **kwargs):
    ...


def Stack(*args, **kwargs):
    ...


def Split(*args, **kwargs):
    ...


def Diffn(*args, **kwargs):
    ...


def main():
    """ Main function, generating and netlisting. """

    params = AmpParams(nmos=PdkNmos(h.NoParams), pmos=PdkPmos(h.NoParams),)
    proto = h.to_proto(h.elaborate(FiveXtorAmp(params)))
    h.netlist(proto, sys.stdout)


if __name__ == "__main__":
    main()
