"""
# Verilog-Format Netlister 
"""
# Local Imports
import vlsir

# Import the base-class
from .base import Netlister


class VerilogNetlister(Netlister):
    """
    # Structural Verilog Netlister 
    """

    @property
    def enum(self):
        """ Get our entry in the `NetlistFormat` enumeration """
        from . import NetlistFormat

        return NetlistFormat.VERILOG

    def write_module_definition(self, module: vlsir.circuit.Module) -> None:
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
        if module.parameters:
            self.writeln("#( ")
            self.indent += 1
            for num, name in enumerate(module.parameters):
                pparam = module.parameters[name]
                comma = "" if num == len(module.parameters) - 1 else ","
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

    def write_instance(self, pinst: vlsir.circuit.Instance) -> None:
        """ Format and write Instance `pinst` """

        # Get its Module or ExternalModule definition
        target = self.resolve_reference(pinst.module)
        module, module_name = target.module, target.module_name

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
    def format_param_type(cls, pparam: vlsir.circuit.Parameter) -> str:
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
    def format_param_decl(cls, name: str, param: vlsir.circuit.Parameter) -> str:
        """ Format a parameter-declaration """
        rv = f"parameter {name}"
        # FIXME: whether to include datatype
        # dtype = cls.format_param_type(param)
        default = cls.get_param_default(param)
        if default is not None:
            rv += f" = {default}"
        return rv

    def format_concat(self, pconc: vlsir.circuit.Concat) -> str:
        """ Format the Concatenation of several other Connections """
        # Verilog { a, b, c } concatenation format
        parts = [self.format_connection(part) for part in pconc.parts]
        return "{" + ", ".join(parts) + "}"

    @classmethod
    def format_port_decl(cls, pport: vlsir.circuit.Port) -> str:
        """ Format a `Port` declaration """

        # First retrieve and check the validity of its direction
        port_type_to_str = {
            vlsir.circuit.Port.Direction.Value("INPUT"): "input",
            vlsir.circuit.Port.Direction.Value("OUTPUT"): "output",
            vlsir.circuit.Port.Direction.Value("INOUT"): "inout",
            vlsir.circuit.Port.Direction.Value("NONE"): "NO_DIRECTION",
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
    def format_signal_decl(cls, psig: vlsir.circuit.Signal) -> str:
        """ Format a `Signal` declaration """
        rv = "wire"
        if psig.width > 1:
            rv += f" [{psig.width-1}:0]"
        rv += f" {psig.name}"
        return rv

    @classmethod
    def format_port_ref(cls, pport: vlsir.circuit.Port) -> str:
        """ Format a reference to a `Port`. 
        Unlike declarations, this just requires the name of its `Signal`. """
        return cls.format_signal_ref(pport.signal)

    @classmethod
    def format_signal_ref(cls, psig: vlsir.circuit.Signal) -> str:
        """ Format a reference to a `Signal`. 
        Unlike declarations, this just requires its name. """
        return psig.name

    @classmethod
    def format_signal_slice(cls, pslice: vlsir.circuit.Slice) -> str:
        """ Format Signal-Slice `pslice` """
        if pslice.top == pslice.bot:  # Single-bit slice
            return f"{pslice.signal}[{pslice.top}]"
        return f"{pslice.signal}[{pslice.top}:{pslice.bot}]"  # Multi-bit slice

    def write_comment(self, comment: str) -> None:
        """ Verilog uses C-style line comments, beginning with `//` """
        self.write(f"// {comment}\n")
