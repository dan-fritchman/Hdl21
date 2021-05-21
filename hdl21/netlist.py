from typing import Tuple
from .module import Module
from .instance import PortRef
from .interface import InterfaceInstance
from .signal import Signal


def to_spectre(design: Module) -> str:
    """ 
    This will netlist a design in the SPECTRE format
    """
    def to_spectre_helper(design: Module) -> Tuple[set, str]:
        net_idx = 0  # Global tracker for net indexing
        def get_name(obj):
            if isinstance(obj, Signal):
                return obj.name
            elif isinstance(obj, PortRef):
                if isinstance(obj.inst, InterfaceInstance):
                    return obj.portname
                else:
                    net_idx += 1
                    return f"net{net_idx}"
            else:
                raise NotImplementedError

        new_insts = set()
        port_intf = [(k, v) for (k, v) in design.interfaces.items() if v.port]
        breakpoint()
        port_intf_sigs = [f"{name}_{sig.name}" for name, intf in port_intf 
            for sig in intf.signals.keys()]
        ports = port_intf_sigs + list(design.ports.keys())
        out = f"subckt {design.name} " +\
                " ".join(ports) + "\n\n"
        for inst_name, inst in design.instances.items():
            out += f'{inst_name} '
            out += ' '.join([get_name(inst.conns[k]) for k in inst.of.ports])
            out += ' ' + inst.of.name + '\n'
            new_insts.add(inst.of)
        out += '\nends\n'
        return new_insts, out

    to_elaborate = set([design])
    netlists = []
    while len(to_elaborate) > 0:
        curr_design = to_elaborate.pop()
        subinsts, curr_netlist = to_spectre_helper(curr_design)
        netlists.append(curr_netlist)
        to_elaborate = to_elaborate | subinsts
    return '\n\n'.join(netlists)

