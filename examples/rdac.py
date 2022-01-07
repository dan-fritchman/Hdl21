import sys
from typing import Dict, Any, Tuple, Sequence

import hdl21 as h


@h.paramclass
class PdkResistorParams:
    w = h.Param(dtype=float, desc="Resistor width (m)")
    l = h.Param(dtype=float, desc="Resistor length (m)")


PdkResistor = h.ExternalModule(
    name="rupolym_m",
    desc="PDK Resistor",
    domain="RDAC's Favorite PDK",
    port_list=[h.Inout(name="PLUS"), h.Inout(name="MINUS")],
    paramtype=PdkResistorParams,
)


@h.paramclass
class PdkMosParams:
    l = h.Param(dtype=float, desc="Channel length (m)")


NchMac = h.ExternalModule(
    name="nch_mac",
    desc="PDK NMOS Transistor",
    port_list=[
        h.Inout(name="D"),
        h.Inout(name="G"),
        h.Inout(name="S"),
        h.Inout(name="B"),
    ],
    paramtype=PdkMosParams,
)
PchMac = h.ExternalModule(
    name="pch_mac",
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
    nseg = h.Param(dtype=int, desc="Number of segments")
    res = h.Param(dtype=h.ExternalModule, desc="Resistor Primitive")
    res_params = h.Param(dtype=PdkResistorParams, desc="Resistor params")
    res_conns = h.Param(
        dtype=Dict[str, str],
        desc="A dict mapping res ports to value P, N and any other res ports to pass through",
    )


@h.generator
def rladder(params: RLadderParams) -> h.Module:

    # Base Module, we'll just declare IO
    @h.module
    class RLadder:
        top = h.Inout()
        bot = h.Inout()
        taps = h.Output(width=params.nseg - 1)

    # A list of all the nets, from the bottom to the top
    netnames = (
        [RLadder.bot]
        + [RLadder.taps[i] for i in range(params.nseg - 1)]
        + [RLadder.top]
    )
    pconns = [
        k for k, v in params.res_conns.items() if v == "P"
    ]  # All the ports of res that connect to P
    nconns = [
        k for k, v in params.res_conns.items() if v == "N"
    ]  # All the ports of res that connect to N
    conns = params.res_conns.copy()  # Make a copy we will mutate
    for i, net in enumerate(netnames[:-1]):
        for k in pconns:
            conns[k] = netnames[i + 1]  # Connect P to the P net for this resistor
        for k in nconns:
            conns[k] = netnames[i]  # Connect N to the N net for this resistor
        # Set each resistor of RLadder as an attibute by calling the generator then adding conns
        RLadder.add(name=f"R{i}", val=params.res(params.res_params)(**conns))

    return RLadder


@h.paramclass
class PassGateParams:
    nmos = h.Param(dtype=h.ExternalModule, desc="NMOS generator")
    nmos_params = h.Param(dtype=PdkMosParams, desc="PMOS Parameters")
    pmos = h.Param(dtype=h.ExternalModule, desc="PMOS generator")
    pmos_params = h.Param(dtype=PdkMosParams, desc="PMOS parameters")


@h.generator
def passgate(params: PassGateParams) -> h.Module:
    @h.module
    class PassGate:
        source = h.Inout()
        drain = h.Inout()

    if params.pmos is not None:
        PassGate.VDD = h.Inout()
        PassGate.en_b = h.Input()
        PassGate.PSW = params.pmos(params.pmos_params)(
            D=PassGate.drain, S=PassGate.source, G=PassGate.en_b, B=PassGate.VDD
        )

    if params.nmos is not None:
        PassGate.VSS = h.Inout()
        PassGate.en = h.Input()
        PassGate.NSW = params.nmos(params.nmos_params)(
            D=PassGate.drain, S=PassGate.source, G=PassGate.en, B=PassGate.VSS
        )

    return PassGate


@h.generator
def mux(params: PassGateParams) -> h.Module:
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
    nbit = h.Param(dtype=int, desc="Number of bits")
    mux_params = h.Param(dtype=PassGateParams, desc="Parameters for the MUX generator")


@h.generator
def mux_tree(params: MuxTreeParams) -> h.Module:
    """ Binary Mux Tree Generator """

    n_inputs = 2 ** params.nbit
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
                name=f"sig_{layer}", val=h.Signal(width=2 ** layer)
            )
        else:
            curr_output = MuxTree.out
        for mux_idx in range(2 ** layer):
            mux_conns = layer_mux_conns.copy()
            mux_conns["sourceA"] = curr_input[2 * mux_idx]
            mux_conns["sourceB"] = curr_input[2 * mux_idx + 1]
            mux_conns["out"] = curr_output[mux_idx]
            MuxTree.add(
                name=f"mux_{layer}_{mux_idx}", val=mux(params.mux_params)(**mux_conns)
            )
        curr_input = curr_output
    return MuxTree


def external_factory(
    name: str, param_names: Sequence[str], port_names: Sequence[str]
) -> Tuple[h.ExternalModule, h.Param]:
    """
    Parameters:
        name: should correspond to the expected name in output netlists
        param_names: A list of parameters instances of this external primitive take
        port_names: A list of port names of this external primitive
    Outputs:
        NewPrimitive: An instance of h.Primitive
        NewParamClass: An instance of h.paramclass
    """
    param_attr_dict = {
        n: h.Param(dtype=Any, desc=f"Gen parameter {n} of {name}") for n in param_names
    }
    # Dynamically create the parameter class, pass it to the h.paramclass decorator function
    custom_params = h.paramclass(type(f"{name}Params", (), param_attr_dict))
    return (
        h.ExternalModule(
            name,
            desc=f"external_module_{name}",
            port_list=[h.Inout(name=n) for n in port_names],
        ),
        custom_params,
    )


def main():
    """ Main function, generating an `rladder` and `mux_tree` and netlisting each. """

    rparams = RLadderParams(
        nseg=15,
        res=PdkResistor,
        res_params=dict(w=4, l=10),
        res_conns=dict(PLUS="P", MINUS="N"),
    )
    mparams = MuxTreeParams(
        nbit=4,
        mux_params=PassGateParams(
            nmos=NchMac,
            nmos_params=PdkMosParams(l=1),
            pmos=PchMac,
            pmos_params=PdkMosParams(l=1),
        ),
    )

    # Convert each to VLSIR protobuf
    proto = h.to_proto([rladder(rparams), mux_tree(mparams)], domain="rdac")

    # And netlist in a handful of formats
    h.netlist(proto, sys.stdout, "verilog")
    h.netlist(proto, sys.stdout, "spectre")
    h.netlist(proto, sys.stdout, "spice")
    h.netlist(proto, sys.stdout, "xyce")


if __name__ == "__main__":
    main()
