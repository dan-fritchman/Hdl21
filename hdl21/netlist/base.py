"""
# Netlister Base Class 

"""

# Std-Lib Imports
from typing import Optional, Tuple, List, Mapping, Union, IO
from enum import Enum
from dataclasses import field
from enum import Enum

# PyPi
from pydantic.dataclasses import dataclass

# Local Imports
import vlsir
from ..proto.to_proto import ProtoExporter
from ..proto.from_proto import ProtoImporter

# Internal type shorthand
ModuleLike = Union[vlsir.circuit.Module, vlsir.circuit.ExternalModule]


class SpicePrimitive(Enum):
    """ Enumerated Spice Primitives and their Instance-Name Prefixes """

    RESISTOR = "r"
    CAPACITOR = "c"
    INDUCTOR = "l"
    MOS = "m"
    DIODE = "d"
    VSOURCE = "v"
    ISOURCE = "i"


@dataclass
class ResolvedModule:
    """ Resolved reference to a `Module` or `ExternalModule`. 
    Includes its netlist-sanitized name, and indication of 
    whether spice-formatting should treat the device as a primitive. """

    module: ModuleLike
    module_name: str
    spice_primitive: Optional[SpicePrimitive]


@dataclass
class Indent:
    """ 
    # Indentation Helper 
    
    Supports in-place addition and subtraction of indentation levels, e.g. via 
    ```python
    indent = Indent()
    indent += 1 # Adds one "tab", or indentation level
    indent += 1 # Adds another
    indent -= 1 # Drops back by one
    ```
    The current indentation-string is available via the `state` attribute. 
    Writers using such an indenter will likely be of the form:
    ```python
    dest.write(f"{indent.state}{content}")
    ```
    """

    # Per-"tab" indentation characters. Defaults to two spaces.
    chars: str = 2 * " "
    # Current (integer) indentation-level, in number of "tabs"
    num: int = field(init=False, default=0)
    # Current indentation-string. Always equals `num * chars`.
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

    def __init__(self, pkg: vlsir.circuit.Package, dest: IO):
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

        # First visit any externally-defined Modules,
        # Ensuring we have their port-orders.
        for emod in self.pkg.ext_modules:
            self.get_external_module(emod)

        # Add some header commentary
        self.write_header()

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

    def get_external_module(self, emod: vlsir.circuit.ExternalModule) -> None:
        """ Visit an ExternalModule definition.
        "Netlisting" these doesn't actually write anything,
        but just stores a reference  in internal dictionary `ext_modules`
        for future references to them. """
        key = (emod.name.domain, emod.name.name)
        if key in self.ext_modules:
            raise RuntimeError(f"Invalid doubly-defined external module {emod}")
        self.ext_modules[key] = emod

    @classmethod
    def get_param_default(cls, pparam: vlsir.circuit.Parameter) -> Optional[str]:
        """ Get the default value of `pparam`. Returns `None` for no default. """
        if pparam.WhichOneof("value") is None:
            return None
        return cls.get_param_value(pparam)

    @classmethod
    def get_param_value(cls, pparam: vlsir.circuit.Parameter) -> str:
        """ Get a string representation of a parameter-value """
        ptype = pparam.WhichOneof("value")
        if ptype == "integer":
            return str(int(pparam.integer))
        if ptype == "double":
            return str(float(pparam.double))
        if ptype == "string":
            return str(pparam.string)
        raise ValueError

    def get_module_name(self, module: vlsir.circuit.Module) -> str:
        """ Create a netlist-compatible name for proto-Module `module` """

        # Create the module name
        # Replace all format-invalid characters with underscores
        name = module.name.split(".")[-1]
        for ch in name:
            if not (ch.isalpha() or ch.isdigit() or ch == "_"):
                name = name.replace(ch, "_")
        return name

    def resolve_reference(self, ref: vlsir.utils.Reference) -> ResolvedModule:
        """ Resolve the `ModuleLike` referent of `ref`. """

        if ref.WhichOneof("to") == "local":  # Internally-defined Module
            module = self.pmodules.get(ref.local, None)
            if module is None:
                raise RuntimeError(f"Invalid undefined Module {ref.local} ")
            return ResolvedModule(
                module=module,
                module_name=self.get_module_name(module),
                spice_primitive=None,
            )

        if ref.WhichOneof("to") == "external":  # Defined outside package

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
                    spice_primitive = SpicePrimitive.CAPACITOR
                elif name == "IdealResistor":
                    module_name = "resistor"
                    spice_primitive = SpicePrimitive.RESISTOR
                elif name == "IdealInductor":
                    module_name = "inductor"
                    spice_primitive = SpicePrimitive.INDUCTOR
                elif name == "VoltageSource":
                    module_name = "vsource"
                    spice_primitive = SpicePrimitive.VSOURCE
                elif name == "CurrentSource":
                    module_name = "isource"
                    spice_primitive = SpicePrimitive.ISOURCE
                else:
                    raise ValueError(f"Unsupported or Invalid Ideal Primitive {ref}")

                # Awkwardly, primitives don't naturally have definitions as
                # either `vlsir.circuit.Module` or `vlsir.circuit.ExternalModule`.
                # So we create one on the fly.
                prim = ProtoImporter.import_primitive(ref.external)
                module = ProtoExporter.export_primitive(prim)
                return ResolvedModule(
                    module=module,
                    module_name=module_name,
                    spice_primitive=spice_primitive,
                )

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
                return ResolvedModule(
                    module=module, module_name=module_name, spice_primitive=None,
                )

        # Not a Module, not an ExternalModule, not sure what it is
        raise ValueError(f"Invalid Module reference {ref}")

    def format_connection(self, pconn: vlsir.circuit.Connection) -> str:
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

    def write_header(self) -> None:
        """ Write header commentary 
        This proves particularly important for many Spice-like formats, 
        which *always* interpret the first line of an input-file as a comment (among many other dumb things). 
        So, always write one there right off the bat. """

        if self.pkg.domain:
            self.write_comment(f"circuit.Package {self.pkg.domain}")
        else:
            self.write_comment(f"Anonymous circuit.Package")
        self.write_comment(f"Written by {self.__class__.__name__}")
        self.write_comment("")
        self.writeln("")

    """ 
    Virtual `format` Methods 
    """

    @classmethod
    def format_param_decl(cls, name: str, param: vlsir.circuit.Parameter) -> str:
        """ Format a named `Parameter` definition """
        raise NotImplementedError

    @classmethod
    def format_port_decl(cls, pport: vlsir.circuit.Port) -> str:
        """ Format a declaration of a `Port` """
        raise NotImplementedError

    @classmethod
    def format_port_ref(cls, pport: vlsir.circuit.Port) -> str:
        """ Format a reference to a `Port` """
        raise NotImplementedError

    @classmethod
    def format_signal_decl(cls, psig: vlsir.circuit.Signal) -> str:
        """ Format a declaration of Signal `psig` """
        raise NotImplementedError

    @classmethod
    def format_signal_ref(cls, psig: vlsir.circuit.Signal) -> str:
        """ Format a reference to Signal `psig` """
        raise NotImplementedError

    @classmethod
    def format_signal_slice(cls, pslice: vlsir.circuit.Slice) -> str:
        """ Format Signal-Slice `pslice` """
        raise NotImplementedError

    def format_concat(self, pconc: vlsir.circuit.Concat) -> str:
        """ Format the Concatenation of several other Connections """
        raise NotImplementedError

    @classmethod
    def format_bus_bit(cls, index: Union[int, str]) -> str:
        """ Format bus-bit `index` """
        raise NotImplementedError

    """ 
    Virtual `write` Methods 
    """

    def write_comment(self, comment: str) -> None:
        """ Format and string a string comment. 
        "Line comments" are the sole supported variety, which fit within a line, and extend to the end of that line. 
        The `write_comment` method assumes responsibility for closing the line. """
        raise NotImplementedError

    def write_module_definition(self, pmodule: vlsir.circuit.Module) -> None:
        """ Write Module `module` """
        raise NotImplementedError

    def write_instance(self, pinst: vlsir.circuit.Instance) -> str:
        """ Write Instance `pinst` """
        raise NotImplementedError

    """ 
    Other Virtual Methods 
    """

    @property
    def enum(self):
        """ Get our entry in the `NetlistFormat` enumeration """
        raise NotImplementedError

