from typing import Tuple, List, Mapping
from .proto import circuit_pb2 as protodefs


class Netlister:
    """
    Base class for different netlisters.
    These methods should all just be string manipulations
    """
    port_type_to_str = {
        protodefs.Port.Direction.INPUT: "input",
        protodefs.Port.Direction.OUTPUT: "output",
        protodefs.Port.Direction.INOUT: "inout",
        protodefs.Port.Direction.NONE: "",
    }

    @classmethod
    def get_module_definiton(cls, name: str, ports: List[protodefs.Port],
                             parameters: Mapping[str, protodefs.Parameter]) -> str:
        raise NotImplementedError

    @classmethod
    def get_signal_definition(cls, signals: List[str]) -> str:
        raise NotImplementedError

    @classmethod
    def get_instance_statement(cls, name: str, module: str, connections: List[Tuple[str, str]],
                               params: List[Tuple[str, str]]) -> str:
        raise NotImplementedError

    @classmethod
    def get_port_name_dir(cls, port: protodefs.Port) -> Tuple[str, str]:
        return port.name, cls.port_type_to_str[port.direction]

    @classmethod
    def parameter_to_str(cls, param: protodefs.Parameter) -> str:
        return str(param.value)


class SpectreNetlister(Netlister):
    """ Netlister for Spectre compatible netlist """
    @classmethod
    def get_module_definiton(cls, name: str, ports: List[protodefs.Port],
                             parameters: Mapping[str, protodefs.Parameter]) -> str:
        out = f"subckt {name} "
        out += " ".join([cls.get_port_name_dir(p)[0] for p in ports])
        out += "\n"
        if len(parameters) > 0:
            out += "parameters "
            out += " ".join([f"{k}={cls.parameter_to_str(v)}" for k, v in parameters.items()])
        return out

    @classmethod
    def get_signal_definition(cls, signals: List[str]) -> str:
        return ""

    @classmethod
    def get_instance_statement(cls, name: str, module: str, connections: List[Tuple[str, str]],
                               params: List[Tuple[str, str]]) -> str:
        return f"{name} " + " ".join([c[1] for c in connections]) + module +\
               " ".join([f'{k}={v}' for k, v in params])


class VerilogNetlister(Netlister):
    """ Netlister to create structural verilog netlists """
    @classmethod
    def get_module_definiton(cls, name: str, ports: List[protodefs.Port],
                             parameters: Mapping[str, protodefs.Parameter]) -> str:
        return f"subckt {name} " + " ".join(ports) + "\n"

    @classmethod
    def get_signal_definition(cls, signals: List[str]) -> str:
        return ""

    @classmethod
    def get_instance_statement(cls, name: str, module: str, connections: List[Tuple[str, str]],
                               params: List[Tuple[str, str]]) -> str:
        return f"{name} " + " ".join([c[1] for c in connections]) + module + \
               " ".join([f'{k}={v}' for k, v in params])


format_to_netlister = dict(spectre=SpectreNetlister, verilog=VerilogNetlister)


def netlist(filename: str, design: protodefs.Package, fmt: str = 'spectre'):
    netlist = ""
    netlister = format_to_netlister[fmt]
    for mod in design.modules:
        netlist += netlister.get_module_definiton(mod.name, mod.ports, mod.default_parameters)
        netlist += netlister.get_signal_definition(mod.signals)
