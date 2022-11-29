"""
# Resistor DAC Example

An example of using `ExternalModule`s representing an implementation technology/ PDK 
in a parametric resistive DAC generator.
"""

import sys
from typing import Dict, Optional

import hdl21 as h
from hdl21.prefix import µ, n


@h.paramclass
class PdkResistorParams:
    """PDK Resistor Parameters"""

    w = h.Param(dtype=h.Prefixed, desc="Resistor width (m)")
    l = h.Param(dtype=h.Prefixed, desc="Resistor length (m)")


PdkResistor = h.ExternalModule(
    name="pdk_resistor",
    desc="PDK Resistor",
    domain="RDAC's Favorite PDK",
    port_list=[h.Inout(name="PLUS"), h.Inout(name="MINUS")],
    paramtype=PdkResistorParams,
)


@h.paramclass
class PdkMosParams:
    """PDK MOSFET Parameters"""

    l = h.Param(dtype=h.Prefixed, desc="Channel length (m)")


Nch = h.ExternalModule(
    name="nch",
    desc="PDK NMOS Transistor",
    port_list=[
        h.Inout(name="D"),
        h.Inout(name="G"),
        h.Inout(name="S"),
        h.Inout(name="B"),
    ],
    paramtype=PdkMosParams,
)
Pch = h.ExternalModule(
    name="pch",
    desc="PDK PMOS Transistor",
    port_list=[
        h.Inout(name="D"),
        h.Inout(name="G"),
        h.Inout(name="S"),
        h.Inout(name="B"),
    ],
    paramtype=PdkMosParams,
)


@h.paramclass
class RLadderParams:
    """# Resistor Ladder Parameters

    Note the use of the `hdl21.Instantiable` type for the unit resistor element.
    This generally means "something we can make an `Instance` of" - most commonly a `Module`.

    Here we will be using a combination of an `ExternalModule` and its parameter-values,
    in something like:

    ```python
    RLadderParams(
        res=PdkResistor(w=4 * µ, l=10 * µ)
    )
    ```
    """

    nseg = h.Param(dtype=int, desc="Number of segments")
    res = h.Param(dtype=h.Instantiable, desc="Unit resistor, with params applied")


@h.generator
def rladder(params: RLadderParams) -> h.Module:
    """# Resistor Ladder Generator"""

    @h.module
    class RLadder:
        # IO
        top = h.Inout()
        bot = h.Inout()
        taps = h.Output(width=params.nseg - 1)

        # Create concatenations for the P and N sides of each resistor
        nsides = h.Concat(bot, taps)
        psides = h.Concat(taps, top)

        # And create our unit resistor array
        runits = params.nseg * params.res(PLUS=psides, MINUS=nsides)

    return RLadder


@h.paramclass
class PassGateParams:
    """# Pass Gate Parameters

    See the commentary on `RLadderParams` above regarding the use of `hdl21.Instantiable`,
    which here serves as the parameter type for each transistor. It will generally be used like:

    ```python
    PassGateParams(
        nmos=Nch(PdkMosParams(l=1 * n)),
        pmos=Pch(PdkMosParams(l=1 * n)),
    )
    ```

    Both `nmos` and `pmos` parameters are `Optional`, which means they can be set to the Python built-in `None` value.
    If either is `None`, its "half" of the pass gate will be omitted.
    Setting *both* to `None` will cause a generator exception.
    """

    nmos = h.Param(dtype=Optional[h.Instantiable], desc="NMOS. Disabled if None.")
    pmos = h.Param(dtype=Optional[h.Instantiable], desc="PMOS. Disabled if None")


@h.generator
def passgate(params: PassGateParams) -> h.Module:
    """# Pass Gate Generator"""
    if params.nmos is None and params.pmos is None:
        raise RuntimeError("A pass gate needs at least *one* transistor!")

    @h.module
    class PassGate:
        source = h.Inout()
        drain = h.Inout()

    if params.pmos is not None:
        PassGate.VDD = h.Inout()
        PassGate.en_b = h.Input()
        PassGate.PSW = params.pmos(
            D=PassGate.drain, S=PassGate.source, G=PassGate.en_b, B=PassGate.VDD
        )

    if params.nmos is not None:
        PassGate.VSS = h.Inout()
        PassGate.en = h.Input()
        PassGate.NSW = params.nmos(
            D=PassGate.drain, S=PassGate.source, G=PassGate.en, B=PassGate.VSS
        )

    return PassGate


@h.generator
def mux(params: PassGateParams) -> h.Module:
    """# Pass-Gate Analog Mux Generator"""

    @h.module
    class Mux:
        sourceA = h.Input()
        sourceB = h.Input()
        out = h.Output()
        ctrl = h.Input()
        ctrl_b = h.Input()

    aconns, bconns = (
        dict(source=Mux.sourceA, drain=Mux.out),
        dict(source=Mux.sourceB, drain=Mux.out),
    )
    if params.pmos is not None:
        Mux.VDD = h.Inout()
        aconns["VDD"] = Mux.VDD
        aconns["en_b"] = Mux.ctrl_b
        bconns["VDD"] = Mux.VDD
        bconns["en_b"] = Mux.ctrl
    if params.nmos is not None:
        Mux.VSS = h.Inout()
        aconns["VSS"] = Mux.VSS
        aconns["en"] = Mux.ctrl
        bconns["VSS"] = Mux.VSS
        bconns["en"] = Mux.ctrl_b
    Mux.passgate_a = passgate(params)(**aconns)
    Mux.passgate_b = passgate(params)(**bconns)
    return Mux


@h.paramclass
class MuxTreeParams:
    """# Mux Tree Parameters"""

    nbit = h.Param(dtype=int, desc="Number of bits")
    mux_params = h.Param(dtype=PassGateParams, desc="Parameters for the MUX generator")


@h.generator
def mux_tree(params: MuxTreeParams) -> h.Module:
    """Binary Mux Tree Generator"""

    n_inputs = 2**params.nbit
    p_ctrl = params.mux_params.nmos is not None
    n_ctrl = params.mux_params.pmos is not None

    # Base module
    @h.module
    class MuxTree:
        out = h.Output()
        v_in = h.Input(width=n_inputs)
        ctrl = h.Input(width=params.nbit)
        ctrl_b = h.Input(width=params.nbit)

    base_mux_conns = dict()
    if p_ctrl:
        MuxTree.VSS = h.Inout()
        base_mux_conns["VSS"] = MuxTree.VSS
    if n_ctrl:
        MuxTree.VDD = h.Inout()
        base_mux_conns["VDD"] = MuxTree.VDD

    # Build the MUX tree layer by layer
    curr_input = MuxTree.v_in
    for layer in range(params.nbit - 1, -1, -1):
        layer_mux_conns = base_mux_conns.copy()
        layer_mux_conns["ctrl"] = MuxTree.ctrl[layer]
        layer_mux_conns["ctrl_b"] = MuxTree.ctrl_b[layer]
        if layer != 0:
            curr_output = MuxTree.add(
                name=f"sig_{layer}", val=h.Signal(width=2**layer)
            )
        else:
            curr_output = MuxTree.out
        for mux_idx in range(2**layer):
            mux_conns = layer_mux_conns.copy()
            mux_conns["sourceA"] = curr_input[2 * mux_idx]
            mux_conns["sourceB"] = curr_input[2 * mux_idx + 1]
            mux_conns["out"] = curr_output[mux_idx]
            MuxTree.add(
                name=f"mux_{layer}_{mux_idx}", val=mux(params.mux_params)(**mux_conns)
            )
        curr_input = curr_output
    return MuxTree


def main():
    """Main function, generating an `rladder` and `mux_tree` and netlisting each."""

    # Create parameter values for each of our top-level generators
    rparams = RLadderParams(
        nseg=15,
        res=PdkResistor(w=4 * µ, l=10 * µ),
    )
    mparams = MuxTreeParams(
        nbit=4,
        mux_params=PassGateParams(
            nmos=Nch(PdkMosParams(l=1 * n)),
            pmos=Pch(PdkMosParams(l=1 * n)),
        ),
    )

    # Netlist in a handful of formats
    duts = [rladder(rparams), mux_tree(mparams)]
    h.netlist(duts, sys.stdout, fmt="verilog")
    h.netlist(duts, sys.stdout, fmt="spectre")
    h.netlist(duts, sys.stdout, fmt="spice")
    h.netlist(duts, sys.stdout, fmt="xyce")


if __name__ == "__main__":
    main()
