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

    def __init__(self, pkg: protodefs.Package):
        self.pkg = pkg
        self.module_names = set()  # Netlisted Module names
        self.pmodules = dict()  # Visited proto-Modules
        self.ext_modules = dict()  # Visited ExternalModules

    def netlist(self) -> str:
        """ Primary API Method.
        Create a netlist for everything in `self.pkg`.
        Returned as a string. """

        # First visit any externally-defined Modules,
        # Ensuring we have their port-orders.
        for emod in self.pkg.ext_modules:
            self.get_external_module(emod)

        # Now do the real stuff,
        # Creating netlist entries for each package-defined Module
        netlist = ""
        for mod in self.pkg.modules:
            netlist += self.get_module_definition(mod)
        return netlist

    def get_external_module(self, emod: protodefs.ExternalModule) -> None:
        """ Visit an ExternalModule definition.
        Stores a reference  in internal dictionary `ext_modules`. """
        if emod.name in self.ext_modules:
            raise RuntimeError(f"Invalid doubly-defined external module {emod}")
        self.ext_modules[emod.name] = emod

    def get_module_definition(self, module: protodefs.Module) -> str:
        raise NotImplementedError

    @classmethod
    def get_signal_definition(cls, signals: List[str]) -> str:
        raise NotImplementedError

    def get_instance(self, pinst: protodefs.Instance) -> str:
        raise NotImplementedError

    @classmethod
    def get_port_name_dir(cls, port: protodefs.Port) -> Tuple[str, str]:
        return port.name, cls.port_type_to_str[port.direction]

    @classmethod
    def get_param_def(cls, name: str, param: protodefs.Parameter) -> str:
        return f"{name} = {cls.get_param_value(param)} "

    def get_param_value(pparam: protodefs.Parameter) -> str:
        """ Get a string representation of a parameter-value """
        ptype = pparam.WhichOneof("value")
        if ptype == "integer":
            return str(int(pparam.integer))
        if ptype == "double":
            return str(float(pparam.double))
        if ptype == "string":
            return f'"{str(pparam.string)}"'
        raise ValueError


class SpectreNetlister(Netlister):
    """Netlister for Spectre compatible netlist"""

    def get_module_name(self, module: protodefs.Module) -> str:
        """ Create a Spectre-compatible name for proto-Module `module` """

        # Create the module name
        # FIXME: mix in its domain
        # qname = module.name
        # module_name = qname.domain + "__" + qname.name
        # module_name = module_name.replace(".", "__")
        return module.name.name.split(".")[-1]

    def get_module_definition(self, module: protodefs.Module) -> str:
        """ Create a Spectre-format definition for proto-Module `module` """

        # Create the module name
        module_name = self.get_module_name(module)
        # Check for double-definition
        if module_name in self.module_names:
            raise RuntimeError(f"Module {module_name} doubly defined")
        # Add to our visited lists
        self.module_names.add(module_name)
        self.pmodules[(module.name.domain, module.name.name)] = module

        # Create the sub-circuit definition header
        out = f"subckt {module_name} \n+  "

        # Create its ports
        for pport in module.ports:
            out += self.get_port(pport) + " "
        out += "\n"

        # Create its parameters, if defined
        if len(module.default_parameters) > 0:
            out += "parameters "
            for name, pparam in module.parameters.items():
                out += self.get_param_def(name, pparam)
            out += "\n"
        out += "\n"

        # Note nothing need be done for internal signals;
        # spice and spectre create these "out of thin air"

        # Create its instances
        for pinst in module.instances:
            out += self.get_instance(pinst)
        out += "\n"

        # Close up the sub-circuit, and return it!
        out += "ends \n\n"
        return out

    def get_connection(self, pconn: protodefs.Connection) -> str:
        """Netlist a `Connection`, a proto `oneof` type,
        which includes signals, slices, and concatenations."""
        # Connections are a proto `oneof` union; figure out which to import
        stype = pconn.WhichOneof("stype")
        if stype == "sig":
            return self.get_signal(pconn.sig)
        if stype == "slice":
            raise RuntimeError(f"Coming Soon!")
            # sname = pconn.slice.signal
        # Concatenations are more complicated and need their own method
        if stype == "concat":
            return self.get_concat(pconn.concat)
        raise ValueError(f"Invalid Connection Type: {pconn}")

    def get_concat(self, pconc: protodefs.Concat) -> str:
        """Netlist a Signal Concatenation"""
        out = ""
        for part in pconc.parts:
            out += self.get_connection(part) + " "
        return out

    @classmethod
    def get_port(cls, pport: protodefs.Port) -> str:
        """Get a netlist `Port` definition
        Note spectre & spice netlists don't include directions,
        so this just requires visiting the underlying `Signal`."""
        return cls.get_signal(pport.signal)

    @classmethod
    def get_signal(cls, psig: protodefs.Signal) -> str:
        """Get a netlist definition for Signal `psig`"""
        if psig.width < 1:
            raise RuntimeError
        if psig.width == 1:  # width==1, i.e. a scalar signal
            return psig.name
        # Vector/ multi "bit" Signal. Creates several spice signals.
        return " ".join([f"{psig.name}[{k}]" for k in reversed(range(psig.width))])

    def get_instance(self, pinst: protodefs.Instance) -> str:
        """Create and return a netlist-string for Instance `pinst`"""

        # Create the instance name
        out = f"x{pinst.name} "
        out += "\n+  "

        # Among the fun parts: finding the right port-order.
        # This requires finding the target Module,
        # which may or may not be defined here in our `pkg`.
        # If it is, use the Module-definition's port order.
        # If not, FIXME(?)
        ref = pinst.module
        if ref.WhichOneof("to") != "qn":  # Only `QualifiedName` is valid and supported
            raise ValueError(f"Invalid reference {ref}")
        if ref.qn.domain == "hdl21.primitives":
            raise RuntimeError(
                f"Not (yet) supported: netlisting hdl21.primitive {pinst}"
            )
        elif not ref.qn.domain:
            # No-domain indicates an ExternalModule.
            # Grab its port-list from our internal dict.
            module = self.ext_modules.get(ref.qn.name, None)
            module_name = ref.qn.name
        elif ref.qn.domain == self.pkg.name:
            # Package-defined Module.
            # Grab from previously imported definitions.
            module = self.pmodules.get((ref.qn.domain, ref.qn.name), None)
            module_name = self.get_module_name(module)
        if module is None:
            raise RuntimeError(f"Instance {pinst} of undefined Module {ref.qn.name}")
        port_order = [pport.signal.name for pport in module.ports]
        # Now write the ports, in this order
        for pname in port_order:
            pconn = pinst.connections.get(pname, None)
            if pconn is None:
                raise RuntimeError(f"Invalid unconnected Port {pname} on {pinst.name}")
            out += self.get_connection(pconn) + " "

        # Write the module-name
        out += "\n+  " + module_name + " "

        # Write the parameter-values
        if len(pinst.parameters):
            raise TabError(f"Coming Soon!")

        # Close it, and return the result
        out += " \n"
        return out


class VerilogNetlister(Netlister):
    """ Netlister to create structural verilog netlists """

    @classmethod
    def get_module_definition(
        cls,
        name: str,
        ports: List[protodefs.Port],
        parameters: Mapping[str, protodefs.Parameter],
    ) -> str:
        return f"subckt {name} " + " ".join(ports) + "\n"

    @classmethod
    def get_signal_definition(cls, signals: List[str]) -> str:
        return ""

    @classmethod
    def get_instance_statement(
        cls,
        name: str,
        module: str,
        connections: List[Tuple[str, str]],
        params: List[Tuple[str, str]],
    ) -> str:
        return (
            f"{name} "
            + " ".join([c[1] for c in connections])
            + module
            + " ".join([f"{k}={v}" for k, v in params])
        )


format_to_netlister = dict(spectre=SpectreNetlister, verilog=VerilogNetlister)


def netlist(filename: str, design: protodefs.Package, fmt: str = "spectre") -> str:
    netlister_cls = format_to_netlister.get(fmt, None)
    if netlister_cls is None:
        raise RuntimeError(
            f"Invalid Netlister format {fmt}: choose one of {format_to_netlister.keys()}"
        )
    netlister = netlister_cls(pkg=design)
    netlist = netlister.netlist()
    print(netlist)  # Give the people somethin for now
    return netlist
