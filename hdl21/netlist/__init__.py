""" 
# Hdl21 Netlisting 

Exports protodefs.Package to a netlist format.
"""

# Std-Lib Imports
from typing import Optional, Tuple, List, Mapping, Union, IO
from enum import Enum
from dataclasses import field

# PyPi
from pydantic.dataclasses import dataclass

# Local Imports
from ..proto.to_proto import ProtoExporter
from ..proto.from_proto import ProtoImporter
from ..proto import circuit_pb2 as protodefs

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
        if self == NetlistFormat.VERILOG:
            return VerilogNetlister
        raise ValueError


# Type-alias for specifying format, either in enum or string terms
NetlistFormatSpec = Union[NetlistFormat, str]


@dataclass
class Indent:
    """ Indentation Helper """

    chars: str = "  "
    num: int = field(init=False, default=0)
    state: str = field(init=False, default="")

    def __post_init_post_parse__(self) -> None:
        self.state = self.chars * self.num

    def __iadd__(self, other: int) -> None:
        """ In-place add, i.e. `indent += 1` """
        self.num += other
        self.state = self.chars * self.num
        return self

    def __isub__(self, other: int) -> None:
        """ In-place subtract, i.e. `indent -= 1` """
        self.num = self.num - other
        if self.num < 0:
            raise ValueError("Negative indentation")
        self.state = self.chars * self.num
        return self


class Netlister:
    """ # Abstract Base `Netlister` Class 

    `Netlister` is not directly instantiable, and none of its sub-classes are intended 
    for usage outside `hdl21.netlist`. The primary API method `netlist` is designed to 
    create, use, and drop a `Netlister` instance. 
    Once instantiated a `Netlister`'s primary API method is `netlist`. 
    This writes all content in its `pkg` field to destination `dest`. 
    
    Internal methods come in two primary flavors:
    * `write_*` methods, which write to `self.dest`. These methods are generally format-specific. 
    * `format_*` methods, which return format-specific strings, but *do not* write to `dest`. 
    * `get_*` methods, which retrieve some internal data, e.g. extracting the type of a `Connection`. 
    """

    enum = None  # Class attr of the `NetlistFormat` enum

    def __init__(self, pkg: protodefs.Package, dest: IO):
        self.pkg = pkg
        self.dest = dest
        self.indent = Indent(chars="  ")
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
        """ Helper/wrapper, passing to `self.dest` """
        self.dest.write(s)

    def writeln(self, s: str) -> None:
        """ Write `s` as a line, at our current `indent` level. """
        self.write(f"{self.indent.state}{s}\n")

    def get_external_module(self, emod: protodefs.ExternalModule) -> None:
        """ Visit an ExternalModule definition.
        "Netlisting" these doesn't actually write anything,
        but just stores a reference  in internal dictionary `ext_modules`
        for future references to them. """
        key = (emod.name.domain, emod.name.name)
        if key in self.ext_modules:
            raise RuntimeError(f"Invalid doubly-defined external module {emod}")
        self.ext_modules[key] = emod

    @classmethod
    def get_param_default(cls, pparam: protodefs.Parameter) -> Optional[str]:
        """ Get the default value of `pparam`. Returns `None` for no default. """
        if pparam.WhichOneof("value") is None:
            return None
        return cls.get_param_value(pparam)

    @classmethod
    def get_param_value(cls, pparam: protodefs.Parameter) -> str:
        """ Get a string representation of a parameter-value """
        ptype = pparam.WhichOneof("value")
        if ptype == "integer":
            return str(int(pparam.integer))
        if ptype == "double":
            return str(float(pparam.double))
        if ptype == "string":
            return str(pparam.string)
        raise ValueError

    def get_module_name(self, module: protodefs.Module) -> str:
        """ Create a netlist-compatible name for proto-Module `module` """

        # Create the module name
        # Replace all format-invalid characters with underscores
        name = module.name.split(".")[-1]
        for ch in name:
            if not (ch.isalpha() or ch.isdigit() or ch == "_"):
                name = name.replace(ch, "_")
        return name

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
                msg = f"Invalid direct-netlisting of physical `hdl21.Primitive` `{ref.external.name}`. "
                msg += "Either compile to a target technology, or replace with an `ExternalModule`. "
                raise RuntimeError(msg)
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
                    msg = f"Invalid Instance of undefined External Module {key}"
                    raise RuntimeError(msg)
                # Check for duplicate names which would conflict from other namespaces
                module_name = ref.external.name
                if (
                    module_name in self.ext_module_names
                    and self.ext_module_names[module_name] is not module
                ):
                    msg = f"Conflicting ExternalModule definitions {module} and {self.ext_module_names[module_name]}"
                    raise RuntimeError(msg)
                self.ext_module_names[module_name] = module

        else:  # Not a Module, not an ExternalModule, not sure what it is
            raise ValueError

        return module, module_name

    def format_connection(self, pconn: protodefs.Connection) -> str:
        """ Format a `Connection` reference. 
        Does not *declare* any new connection objects, but generates references to existing ones. """
        # Connections are a proto `oneof` union
        # which includes signals, slices, and concatenations.
        # Figure out which to import

        stype = pconn.WhichOneof("stype")
        if stype == "sig":
            return self.format_signal_ref(pconn.sig)
        if stype == "slice":
            return self.format_signal_slice(pconn.slice)
        if stype == "concat":
            return self.format_concat(pconn.concat)
        raise ValueError(f"Invalid Connection Type {stype} for Connection {pconn}")

    """ 
    Virtual `format` Methods 
    """

    @classmethod
    def format_param_decl(cls, name: str, param: protodefs.Parameter) -> str:
        """ Format a named `Parameter` definition """
        raise NotImplementedError

    @classmethod
    def format_port_decl(cls, pport: protodefs.Port) -> str:
        """ Format a declaration of a `Port` """
        raise NotImplementedError

    @classmethod
    def format_port_ref(cls, pport: protodefs.Port) -> str:
        """ Format a reference to a `Port` """
        raise NotImplementedError

    @classmethod
    def format_signal_decl(cls, psig: protodefs.Signal) -> str:
        """ Format a declaration of Signal `psig` """
        raise NotImplementedError

    @classmethod
    def format_signal_ref(cls, psig: protodefs.Signal) -> str:
        """ Format a reference to Signal `psig` """
        raise NotImplementedError

    @classmethod
    def format_signal_slice(cls, pslice: protodefs.Slice) -> str:
        """ Format Signal-Slice `pslice` """
        raise NotImplementedError

    def format_concat(self, pconc: protodefs.Concat) -> str:
        """ Format the Concatenation of several other Connections """
        raise NotImplementedError

    @classmethod
    def format_bus_bit(cls, index: Union[int, str]) -> str:
        """ Format bus-bit `index` """
        raise NotImplementedError

    """ 
    Virtual `write` Methods 
    """

    def write_module_definition(self, pmodule: protodefs.Module) -> None:
        """ Write Module `module` """
        raise NotImplementedError

    def write_instance(self, pinst: protodefs.Instance) -> str:
        """ Write Instance `pinst` """
        raise NotImplementedError


class SpectreNetlister(Netlister):
    """Netlister for Spectre compatible netlist"""

    enum = NetlistFormat.SPECTRE  # Class attr of the `NetlistFormat` enum

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
                self.write(self.format_port_decl(pport) + " ")
            self.write("\n")
        else:
            self.write("+  // No ports \n")

        # Create its parameters, if defined
        if module.default_parameters:
            self.write("parameters ")
            for name, pparam in module.parameters.items():
                self.write(self.format_param_decl(name, pparam))
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
                self.write(self.format_connection(pconn) + " ")
            self.write(" ) \n")
        else:
            self.write("+  // No ports \n")

        # Write the module-name
        self.write("+  " + module_name + " \n")

        if pinst.parameters:  # Write the parameter-values
            self.write("+  ")
            for pname, pparam in pinst.parameters.items():
                pval = self.get_param_value(pparam)
                self.write(f"{pname}={pval} ")
            self.write(" \n")
        else:
            self.write("+  // No parameters \n")

        # And add a post-instance blank line
        self.write("\n")

    def format_concat(self, pconc: protodefs.Concat) -> str:
        """ Format the Concatenation of several other Connections """
        out = ""
        for part in pconc.parts:
            out += self.format_connection(part) + " "
        return out

    @classmethod
    def format_port_decl(cls, pport: protodefs.Port) -> str:
        """ Get a netlist `Port` definition """
        return cls.format_signal_ref(pport.signal)

    @classmethod
    def format_port_ref(cls, pport: protodefs.Port) -> str:
        """ Get a netlist `Port` reference """
        return cls.format_signal_ref(pport.signal)

    @classmethod
    def format_signal_ref(cls, psig: protodefs.Signal) -> str:
        """ Get a netlist definition for Signal `psig` """
        if psig.width < 1:
            raise RuntimeError
        if psig.width == 1:  # width==1, i.e. a scalar signal
            return psig.name
        # Vector/ multi "bit" Signal. Creates several spice signals.
        return " ".join(
            [f"{psig.name}{cls.format_bus_bit(k)}" for k in reversed(range(psig.width))]
        )

    @classmethod
    def format_signal_slice(cls, pslice: protodefs.Slice) -> str:
        """Get a netlist definition for Signal-Slice `pslice`"""
        base = pslice.signal
        indices = list(reversed(range(pslice.bot, pslice.top + 1)))
        if not len(indices):
            raise RuntimeError(f"Attempting to netlist empty slice {pslice}")
        return " ".join([f"{base}{cls.format_bus_bit(k)}" for k in indices])

    @classmethod
    def format_bus_bit(cls, index: Union[int, str]) -> str:
        """ Format-specific string-representation of a bus bit-index"""
        # Spectre netlisting uses an underscore prefix, e.g. `bus_0`
        return "_" + str(index)


class VerilogNetlister(Netlister):
    """ Netlister to create structural verilog netlists """

    enum = NetlistFormat.VERILOG  # Class attr of the `NetlistFormat` enum

    def write_module_definition(self, module: protodefs.Module) -> None:
        """ Create a Verilog module definition for proto-Module `module` """

        # Create the module name
        module_name = self.get_module_name(module)
        # Check for double-definition
        if module_name in self.module_names:
            raise RuntimeError(f"Module {module_name} doubly defined")
        # Add to our visited lists
        self.module_names.add(module_name)
        self.pmodules[module.name] = module

        # Create the module header
        self.writeln(f"module {module_name}")

        # Create its parameters, if defined
        if module.default_parameters:
            self.writeln("#( ")
            self.indent += 1
            for num, name in enumerate(module.default_parameters):
                pparam = module.default_parameters[name]
                comma = "" if num == len(module.default_parameters) - 1 else ","
                self.writeln(self.format_param_decl(name, pparam) + comma)
            self.indent -= 1
            self.writeln(") ")
        else:
            self.writeln("// No parameters ")

        if module.ports:  # Create its ports
            # Don't forget, a trailing comma after the last one is fatal to high-tech Verilog parsers!
            self.writeln("( ")
            self.indent += 1
            for num, pport in enumerate(module.ports):
                comma = "" if num == len(module.ports) - 1 else ","
                self.writeln(self.format_port_decl(pport) + comma)
            self.indent -= 1
            self.writeln("); ")
        else:
            self.writeln("// No ports ")

        self.writeln("")  # Blank line to end "header" facets
        self.indent += 1

        if module.signals:  # Create Signal declarations
            self.writeln("// Signal Declarations")
            for psig in module.signals:
                self.writeln(self.format_signal_decl(psig) + "; ")
        else:
            self.writeln("// No Signal Declarations")

        if module.instances:  # Create its instances
            self.writeln("")
            self.writeln("// Instance Declarations")
            for pinst in module.instances:
                self.write_instance(pinst)
        else:
            self.writeln("// No Instances")

        # Close up the module
        self.indent -= 1
        self.writeln("")  # Blank before `endmodule`
        self.writeln(f"endmodule // {module_name} \n\n")

    def write_instance(self, pinst: protodefs.Instance) -> None:
        """ Format and write Instance `pinst` """

        # Get its Module or ExternalModule definition
        module, module_name = self.resolve_reference(pinst.module)

        # Write the module-name
        self.writeln(module_name)

        if pinst.parameters:  # Write the parameter-values
            self.writeln("#( ")
            self.indent += 1
            for pname, pparam in pinst.parameters.items():
                pval = self.get_param_value(pparam)
                self.writeln(f"{pname}={pval} ")
            self.indent -= 1
            self.writeln(") ")
        else:
            self.writeln("// No parameters ")

        # Write the instance name
        self.writeln(pinst.name)

        if module.ports:  # Write connections, by-name, in-order
            self.writeln("( ")
            self.indent += 1
            # Get `module`'s port-order
            port_order = [pport.signal.name for pport in module.ports]
            # And write the Instance ports, in that order
            for num, pname in enumerate(port_order):
                pconn = pinst.connections.get(pname, None)
                if pconn is None:
                    raise RuntimeError(f"Unconnected Port {pname} on {pinst.name}")
                # Again a trailing comma after the last one is fatal!
                comma = "" if num == len(port_order) - 1 else ","
                self.writeln(f".{pname}({self.format_connection(pconn)}){comma} ")
            # Close up the ports
            self.indent -= 1
            self.writeln("); ")
        else:
            self.writeln("// No ports ")

        self.writeln("")  # Post-Instance blank line

    @classmethod
    def format_param_type(cls, pparam: protodefs.Parameter) -> str:
        """ Verilog type-string for `Parameter` `param`. """
        ptype = pparam.WhichOneof("value")
        if ptype == "integer":
            return "longint"
        if ptype == "double":
            return "real"
        if ptype == "string":
            return "string"
        raise ValueError

    @classmethod
    def format_param_decl(cls, name: str, param: protodefs.Parameter) -> str:
        """ Format a parameter-declaration """
        rv = f"parameter {name}"
        # FIXME: whether to include datatype
        # dtype = cls.format_param_type(param)
        default = cls.get_param_default(param)
        if default is not None:
            rv += f" = {default}"
        return rv

    def format_concat(self, pconc: protodefs.Concat) -> str:
        """ Format the Concatenation of several other Connections """
        # Verilog { a, b, c } concatenation format
        parts = [self.format_connection(part) for part in pconc.parts]
        return "{" + ", ".join(parts) + "}"

    @classmethod
    def format_port_decl(cls, pport: protodefs.Port) -> str:
        """ Format a `Port` declaration """

        # First retrieve and check the validity of its direction
        port_type_to_str = {
            protodefs.Port.Direction.Value("INPUT"): "input",
            protodefs.Port.Direction.Value("OUTPUT"): "output",
            protodefs.Port.Direction.Value("INOUT"): "inout",
            protodefs.Port.Direction.Value("NONE"): "NO_DIRECTION",
        }
        dir_ = port_type_to_str.get(pport.direction, None)
        if dir_ is None:
            msg = f"Invalid Verilog netlisting for unknown Port direction {pport.direction}"
            raise RuntimeError(msg)
        if dir_ == "NO_DIRECTION":
            msg = f"Invalid Verilog netlisting for undirected Port {pport}"
            raise RuntimeError(msg)

        return dir_ + " " + cls.format_signal_decl(pport.signal)

    @classmethod
    def format_signal_decl(cls, psig: protodefs.Signal) -> str:
        """ Format a `Signal` declaration """
        rv = "wire"
        if psig.width > 1:
            rv += f" [{psig.width-1}:0]"
        rv += f" {psig.name}"
        return rv

    @classmethod
    def format_port_ref(cls, pport: protodefs.Port) -> str:
        """ Format a reference to a `Port`. 
        Unlike declarations, this just requires the name of its `Signal`. """
        return cls.format_signal_ref(pport.signal)

    @classmethod
    def format_signal_ref(cls, psig: protodefs.Signal) -> str:
        """ Format a reference to a `Signal`. 
        Unlike declarations, this just requires its name. """
        return psig.name

    @classmethod
    def format_signal_slice(cls, pslice: protodefs.Slice) -> str:
        """ Format Signal-Slice `pslice` """
        base = pslice.signal
        indices = list(reversed(range(pslice.bot, pslice.top + 1)))
        if not len(indices):
            raise RuntimeError(f"Attempting to netlist empty slice {pslice}")
        return " ".join([f"{base}{cls.format_bus_bit(k)}" for k in indices])

    @classmethod
    def format_bus_bit(cls, index: Union[int, str]) -> str:
        """ Format-specific string-representation of a bus bit-index"""
        # Spectre netlisting uses an underscore prefix, e.g. `bus_0`
        return "_" + str(index)

    @classmethod
    def format_bus_bit(cls, index: Union[int, str]) -> str:
        """ Format-specific string-representation of a bus bit-index"""
        # Square-bracket notation, e.g. `signal[0]`
        return "[" + str(index) + "]"


def netlist(
    pkg: protodefs.Package, dest: IO, fmt: NetlistFormatSpec = "spectre"
) -> None:
    """ Netlist proto-Package `pkg` to destination `dest`. 

    Example usages: 
    ```python
    h.netlist(pkg, dest=open('mynetlist.v', 'w'), fmt='verilog')
    ```
    ```python
    s = StringIO()
    h.netlist(pkg, dest=s, fmt='spectre')
    ```
    ```python
    import sys
    h.netlist(pkg, dest=sys.stdout, fmt='spice')
    ```

    Primary argument `pkg` must be a `protodefs.Package`.  
    Destination `dest` may be anything that supports the `typing.IO` interface, 
    commonly including open file-handles. `StringIO` is particularly helpful 
    for producing a netlist in an in-memory string.  
    Format-specifier `fmt` may be any of the `NetlistFormatSpec` enumerated values 
    or their string equivalents.
    """
    fmt_enum = NetlistFormat.get(fmt)
    netlister_cls = fmt_enum.netlister()
    netlister = netlister_cls(pkg, dest)
    netlister.netlist()

