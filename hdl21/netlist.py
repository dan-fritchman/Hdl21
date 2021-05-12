from typing import Tuple
from .module import Module


def to_spectre(design: Module) -> str:
    """ 
    This will netlist a design in the SPECTRE format
    """
    def to_spectre_helper(design: Module) -> Tuple[set, str]:
        new_insts = set()
        out = f"subckt {design.name} " +\
                " ".join([k for k in design.ports.keys()]) + "\n\n"
        for inst_name, inst in design.instances.items():
            out += f'{inst_name} '
            out += ' '.join([inst.conns[k].name for k in inst.of.ports])
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

