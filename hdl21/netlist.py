from typing import Tuple, List, Mapping, Union, IO
from enum import Enum

from .proto.to_proto import ProtoExporter
from .proto.from_proto import ProtoImporter
from .proto import circuit_pb2 as protodefs

# Internal type shorthand
ModuleLike = Union[protodefs.Module, protodefs.ExternalModule]


class NetlistFormat(Enum):
    """ Enumeration of available formats. 
    Includes string-value conversion/ generation. """

    SPECTRE = "spectre"
    VERILOG = "verilog"

    @staticmethod
    def get(spec: "NetlistFormatSpec") -> "NetlistFormat":
        """ Get the format specified by `spec`, in either enum or string terms. 
        Only does real work in the case when `spec` is a string, otherwise returns it unchanged. """
        if isinstance(spec, (NetlistFormat, str)):
            return NetlistFormat(spec)
        raise TypeError

    def netlister(self) -> type:
        """ Get the paired netlister-class """
        if self == NetlistFormat.SPECTRE:
            return SpectreNetlister
        if self == NetlistFormat.VE:
            return VerilogNetlister
        raise ValueError


# Type-alias for specifying format, either in enum or string terms
NetlistFormatSpec = Union[NetlistFormat, str]


class Netlister:
    """
    Base class for different netlisters.
    These methods should all just be string manipulations
    """

    enum = None  # Class attr of the `NetlistFormat` enum

    port_type_to_str = {
        protodefs.Port.Direction.INPUT: "input",
        protodefs.Port.Direction.OUTPUT: "output",
        protodefs.Port.Direction.INOUT: "inout",
        protodefs.Port.Direction.NONE: "",
    }

    def __init__(self, pkg: protodefs.Package, dest: IO):
        self.pkg = pkg
        self.dest = dest
        self.module_names = set()  # Netlisted Module names
        self.pmodules = dict()  # Visited proto-Modules
        self.ext_modules = dict()  # Visited ExternalModules
        self.ext_module_names = (
            dict()
        )  # Visited ExternalModule names, checked for duplicates

    def netlist(self) -> None:
        """ Primary API Method.
        Convert everything in `self.pkg` and write to `self.dest`. """

        if self.pkg.ext_sources:
            raise RuntimeError(f"External sources not (yet) supported")

        # First visit any externally-defined Modules,
        # Ensuring we have their port-orders.
        for emod in self.pkg.ext_modules:
            self.get_external_module(emod)

        # Now do the real stuff,
        # Creating netlist entries for each package-defined Module
        for mod in self.pkg.modules:
            self.write_module_definition(mod)
        # And ensure all output makes it to `self.dest`
        self.dest.flush()

    def write(self, s: str) -> None:
        # Helper/wrapper, passing to `self.dest`
        self.dest.write(s)

    def get_external_module(self, emod: protodefs.ExternalModule) -> None:
        """ Visit an ExternalModule definition.
        "Netlisting" these doesn't actually write anything,
        but just stores a reference  in internal dictionary `ext_modules`
        for future references to them. """
        key = (emod.name.domain, emod.name.name)
        if key in self.ext_modules:
            raise RuntimeError(f"Invalid doubly-defined external module {emod}")
        self.ext_modules[key] = emod

    def write_module_definition(self, module: protodefs.Module) -> None:
        raise NotImplementedError

    @classmethod
    def get_signal_definition(cls, signals: List[str]) -> str:
        raise NotImplementedError

    def write_instance(self, pinst: protodefs.Instance) -> str:
        raise NotImplementedError

    @classmethod
    def get_port_name_dir(cls, port: protodefs.Port) -> Tuple[str, str]:
        return port.name, cls.port_type_to_str[port.direction]

    @classmethod
    def get_param_def(cls, name: str, param: protodefs.Parameter) -> str:
        """ Get a `param=value` definition-pair """
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

    enum = NetlistFormat.SPECTRE  # Class attr of the `NetlistFormat` enum

    def get_module_name(self, module: protodefs.Module) -> str:
        """ Create a Spectre-compatible name for proto-Module `module` """

        # Create the module name
        # Replace all format-invalid characters with underscores
        name = module.name.split(".")[-1]
        for ch in name:
            if not (ch.isalpha() or ch.isdigit() or ch == "_"):
                name = name.replace(ch, "_")
        return name

    def write_module_definition(self, module: protodefs.Module) -> None:
        """ Create a Spectre-format definition for proto-Module `module` """

        # Create the module name
        module_name = self.get_module_name(module)
        # Check for double-definition
        if module_name in self.module_names:
            raise RuntimeError(f"Module {module_name} doubly defined")
        # Add to our visited lists
        self.module_names.add(module_name)
        self.pmodules[module.name] = module

        # Create the sub-circuit definition header
        self.write(f"subckt {module_name} \n")

        if module.ports:  # Create its ports
            self.write("+  ")
            for pport in module.ports:
                self.write(self.get_port(pport) + " ")
            self.write("\n")
        else:
            self.write("+  // No ports \n")

        # Create its parameters, if defined
        if module.default_parameters:
            self.write("parameters ")
            for name, pparam in module.parameters.items():
                self.write(self.get_param_def(name, pparam))
            self.write("\n")
        else:
            self.write("+  // No parameters \n")

        self.write("\n")  # End "header" facets
        # Note nothing need be done for internal signals;
        # spice and spectre create these "out of thin air"

        # Create its instances
        for pinst in module.instances:
            self.write_instance(pinst)
        self.write("\n")

        # Close up the sub-circuit
        self.write("ends \n\n")

    def get_connection(self, pconn: protodefs.Connection) -> str:
        """ Netlist a `Connection`, a proto `oneof` type,
        which includes signals, slices, and concatenations. """
        # Connections are a proto `oneof` union; figure out which to import
        stype = pconn.WhichOneof("stype")
        if stype == "sig":
            return self.get_signal(pconn.sig)
        if stype == "slice":
            return self.get_signal_slice(pconn.slice)
        # Concatenations are more complicated and need their own method
        if stype == "concat":
            return self.get_concat(pconn.concat)
        raise ValueError(f"Invalid Connection Type: {pconn}")

    def get_concat(self, pconc: protodefs.Concat) -> str:
        """ Netlist a Signal Concatenation """
        out = ""
        for part in pconc.parts:
            out += self.get_connection(part) + " "
        return out

    @classmethod
    def get_port(cls, pport: protodefs.Port) -> str:
        """ Get a netlist `Port` definition
        Note spectre & spice netlists don't include directions,
        so this just requires visiting the underlying `Signal`. """
        return cls.get_signal(pport.signal)

    @classmethod
    def get_signal(cls, psig: protodefs.Signal) -> str:
        """ Get a netlist definition for Signal `psig` """
        if psig.width < 1:
            raise RuntimeError
        if psig.width == 1:  # width==1, i.e. a scalar signal
            return psig.name
        # Vector/ multi "bit" Signal. Creates several spice signals.
        return " ".join(
            [f"{psig.name}{cls.bus_bit(k)}" for k in reversed(range(psig.width))]
        )

    @classmethod
    def get_signal_slice(cls, pslice: protodefs.Slice) -> str:
        """Get a netlist definition for Signal-Slice `pslice`"""
        base = pslice.signal
        indices = list(reversed(range(pslice.bot, pslice.top + 1)))
        if not len(indices):
            raise RuntimeError(f"Attempting to netlist empty slice {pslice}")
        return " ".join([f"{base}{cls.bus_bit(k)}" for k in indices])

    @classmethod
    def bus_bit(cls, index: Union[int, str]) -> str:
        """ Format-specific string-representation of a bus bit-index"""
        # Spectre netlisting uses an underscore prefix, e.g. `bus_0`
        return "_" + str(index)

    def write_instance(self, pinst: protodefs.Instance) -> None:
        """Create and return a netlist-string for Instance `pinst`"""

        # Create the instance name
        self.write(pinst.name + "\n")

        # Get its Module or ExternalModule definition, primarily for sake of port-order
        module, module_name = self.resolve_reference(pinst.module)

        if module.ports:
            self.write("+  ( ")
            # Get `module`'s port-order
            port_order = [pport.signal.name for pport in module.ports]
            # And write the Instance ports, in that order
            for pname in port_order:
                pconn = pinst.connections.get(pname, None)
                if pconn is None:
                    raise RuntimeError(f"Unconnected Port {pname} on {pinst.name}")
                self.write(self.get_connection(pconn) + " ")
            self.write(" ) \n")
        else:
            self.write("+  // No ports \n")

        # Write the module-name
        self.write("+  " + module_name + " \n")

        if pinst.parameters:  # Write the parameter-values
            self.write("+  ")
            for pname, pparam in pinst.parameters.items():
                pval = self.get_parameter_val(pparam)
                self.write(f"{pname}={pval} ")
            self.write(" \n")
        else:
            self.write("+  // No parameters \n")

        # And add a post-instance blank line
        self.write("\n")

    def resolve_reference(self, ref: protodefs.Reference) -> Tuple[ModuleLike, str]:
        """ Resolve the `ModuleLike` referent of `ref`, along with its name. """

        if ref.WhichOneof("to") == "local":  # Internally-defined Module
            module = self.pmodules.get(ref.local, None)
            if module is None:
                raise RuntimeError(f"Invalid undefined Module {ref.local} ")
            module_name = self.get_module_name(module)

        elif ref.WhichOneof("to") == "external":  # Defined outside package

            # First check the priviledged/ internally-defined domains
            if ref.external.domain == "hdl21.primitives":
                raise RuntimeError(
                    f"Direct netlisting of `hdl21.primitive` {ref.external.name} not (yet) supported"
                )
            if ref.external.domain == "hdl21.ideal":
                # Ideal elements
                name = ref.external.name

                # Sort out the spectre-format name
                if name == "IdealCapacitor":
                    module_name = "capacitor"
                elif name == "IdealResistor":
                    module_name = "resistor"
                elif name == "IdealInductor":
                    module_name = "inductor"
                elif name == "VoltageSource":
                    module_name = "vsource"
                else:
                    raise ValueError(f"Unsupported or Invalid Ideal Primitive {ref}")

                # Awkardly, primitives don't naturally have definitions as
                # either `protodefs.Module` or `protodefs.ExternalModule`.
                # So we create one on the fly.
                prim = ProtoImporter.import_primitive(ref.external)
                module = ProtoExporter.export_primitive(prim)

            else:  # External Module
                key = (ref.external.domain, ref.external.name)
                module = self.ext_modules.get(key, None)
                if module is None:
                    raise RuntimeError(
                        f"Invalid Instance of undefined External Module {key}"
                    )
                # Check for duplicate names which would conflict from other namespaces
                module_name = ref.external.name
                if (
                    module_name in self.ext_module_names
                    and self.ext_module_names[module_name] is not module
                ):
                    raise RuntimeError(
                        f"Conflicting ExternalModule definitions {module} and {self.ext_module_names[module_name]}"
                    )
                self.ext_module_names[module_name] = module

        else:  # Not a Module, not an ExternalModule, not sure what it is
            raise ValueError

        return module, module_name

    def get_parameter_val(self, pparam: protodefs.Parameter) -> Union[int, float, str]:
        """ Convert proto-parameter `pparam` into Python-string-ifiable types """
        ptype = pparam.WhichOneof("value")
        if ptype == "integer":
            return int(pparam.integer)
        if ptype == "double":
            return float(pparam.double)
        if ptype == "string":
            return str(pparam.string)
        raise ValueError


class VerilogNetlister(Netlister):
    """ Netlister to create structural verilog netlists """

    enum = NetlistFormat.VERILOG  # Class attr of the `NetlistFormat` enum

    @classmethod
    def write_module_definition(
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
    def write_instance(
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


def netlist(
    pkg: protodefs.Package, dest: IO, fmt: NetlistFormatSpec = "spectre"
) -> None:
    """ Netlist proto-Package `pkg` to destination `dest`. """
    fmt_enum = NetlistFormat.get(fmt)
    netlister_cls = fmt_enum.netlister()
    netlister = netlister_cls(pkg, dest)
    netlister.netlist()

