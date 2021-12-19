""" 
# Spice Format Netlisting
"""

# Std-Lib Imports
from typing import Union

# Local Imports
from ..proto import circuit_pb2 as protodefs

# Import the base-class
from .base import Netlister, ResolvedModule


class SpiceNetlister(Netlister):
    """ Netlister for generic SPICE netlist (ngspice, xyce)"""

    @property
    def enum(self):
        """ Get our entry in the `NetlistFormat` enumeration """
        from . import NetlistFormat

        return NetlistFormat.SPICE

    def write_module_definition(self, module: protodefs.Module) -> None:
        # Create the module name
        module_name = self.get_module_name(module)
        # Check for double-definition
        if module_name in self.module_names:
            raise RuntimeError(f"Module {module_name} doubly defined")
        # Add to our visited lists
        self.module_names.add(module_name)
        self.pmodules[module.name] = module

        # Create the sub-circuit definition header
        self.write(f".SUBCKT {module_name} \n")

        if module.ports:  # Create its ports
            self.write("+ ")
            for pport in module.ports:
                self.write(self.format_port_decl(pport) + " ")
            self.write("\n")
        else:
            self.write("+ * No ports\n")

        # Create its parameters, if defined
        if module.default_parameters:
            # Parameter format:
            # + name1=val1 name2=val2 name3=val3 \n
            self.write("+ ")
            for name, pparam in module.parameters.items():
                self.write(self.format_param_decl(name, pparam))
            self.write("\n")
        else:
            self.write("+ * No parameters\n")
        self.write("\n")

        # Create its instances
        for pinst in module.instances:
            self.write_instance(pinst)

        # Close up the sub-circuit
        self.write(".ENDS\n\n")

    def write_instance_name(
        self, pinst: protodefs.Instance, target: ResolvedModule
    ) -> None:
        """ Write the instance-name line for `pinst`, including the SPICE-dictated primitive-prefix. """
        prim = target.spice_primitive
        prefix = "x" if prim is None else prim.value()
        self.write(f"{prefix}{pinst.name} \n")

    def write_instance(self, pinst: protodefs.Instance) -> None:
        """ Create and return a netlist-string for Instance `pinst`"""

        # Get its Module or ExternalModule definition, primarily for sake of port-order
        target = self.resolve_reference(pinst.module)
        module = target.module

        # Create the instance name
        self.write_instance_name(pinst, target)

        if module.ports:
            self.write("+ ")
            # Get `module`'s port-order
            port_order = [pport.signal.name for pport in module.ports]
            # And write the Instance ports, in that order
            for pname in port_order:
                pconn = pinst.connections.get(pname, None)
                if pconn is None:
                    raise RuntimeError(f"Unconnected Port {pname} on {pinst.name}")
                self.write(self.format_connection(pconn) + " ")
            self.write("\n")
        else:
            self.write("+ * No ports \n")

        if target.spice_primitive is None:
            # Write the module-name
            self.write("+ " + target.module_name + " \n")

        if pinst.parameters:  # Write the parameter-values
            self.write("+ ")
            # Parameter format:
            # + name1=val1 name2=val2 name3=val3 \n
            for pname, pparam in pinst.parameters.items():
                pval = self.get_param_value(pparam)
                self.write(f"{pname}={pval} ")
            self.write("\n")
        else:
            self.write("+ * No parameters \n")
        self.write("\n")

    # TODO: copied from Spectre implementation, need test cases to exercise
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
        """ Get a netlist definition for Signal-Slice `pslice` """
        base = pslice.signal
        indices = list(reversed(range(pslice.bot, pslice.top + 1)))
        if not len(indices):
            raise RuntimeError(f"Attempting to netlist empty slice {pslice}")
        return " ".join([f"{base}{cls.format_bus_bit(k)}" for k in indices])

    @classmethod
    def format_bus_bit(cls, index: Union[int, str]) -> str:
        """ Format-specific string-representation of a bus bit-index """
        # Spectre netlisting uses an underscore prefix, e.g. `bus_0`
        return "_" + str(index)

    @classmethod
    def format_param_decl(cls, name: str, param: protodefs.Parameter) -> str:
        """ Format a parameter-declaration """
        default = cls.get_param_default(param)
        if default is None:
            msg = f"Invalid non-default parameter {param} for Spice netlisting"
            raise RuntimeError(msg)
        return f"{name}={default}"
