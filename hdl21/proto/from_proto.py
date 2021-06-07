"""
hdl21 ProtoBuf Import 
"""
from types import SimpleNamespace
from typing import Union, Any

# Local imports
# Proto-definitions
from . import circuit_pb2 as protodefs

# HDL
from ..module import Module
from ..instance import Instance
from ..signal import Signal, Port, PortDir, Slice, Concat
from .. import primitives
from ..primitives import Primitive


def from_proto(pkg: protodefs.Package) -> SimpleNamespace:
    """ Convert Proto-defined Package `pkg` to a namespace-full of Modules. """
    importer = ProtoImporter(pkg)
    return importer.import_()


class ProtoImporter:
    """ Protobuf Package Importer. 
    Collects all `Modules` defined in Protobuf-sourced primary-argument `pkg` into a Python `types.SimpleNamespace`. """

    def __init__(self, pkg: protodefs.Package):
        self.pkg = pkg
        self.modules = dict()  # Dict of qual-names to Modules
        self.ns = SimpleNamespace()
        self.ns.name = pkg.name

    def import_(self) -> SimpleNamespace:
        """ Import the top-level `Package` to a Python namespace """
        # Walk through each proto-defined Module
        for pmod in self.pkg.modules:
            self.import_module(pmod)
        # Return our collected namespace
        return self.ns

    def import_module(self, pmod: protodefs.Module) -> Module:
        """ Convert Proto-Module `pmod` to an `hdl21.Module` """
        if (pmod.name.domain, pmod.name.name) in self.modules:
            raise RuntimeError(
                f"Proto Import Error: Redefined Module {(pmod.name.domain, pmod.name.name)}"
            )

        # Create the Module
        module = Module()
        # Get or create its namespace, and set its name
        ns = self.ns
        parts = pmod.name.name.split(".")  # Path-parts are dot-separated
        for part in parts[:-1]:
            attr = getattr(ns, part, None)
            if attr is None:  # Create a new Namespce
                new_ns = SimpleNamespace()
                new_ns.name = part
                setattr(ns, part, new_ns)
                ns = new_ns
            elif isinstance(attr, SimpleNamespace):
                ns = attr
            else:
                raise RuntimeError(
                    f"Invalid Module path-name {pmod.name.name} overwriting {attr}"
                )
        module.name = parts[-1]

        # Import its ports
        for pport in pmod.ports:
            dir_ = self.import_port_dir(pport)
            port = Port(
                name=pport.signal.name, width=pport.signal.width, direction=dir_,
            )
            module.add(port)

        # Import its signals
        for psig in pmod.signals:
            sig = Signal(name=psig.name, width=psig.width)
            module.add(sig)

        # Lap through instances, connecting them, creating internal Signals if necessary (bleh)
        for pinst in pmod.instances:
            inst = self.import_instance(pinst)
            module.add(inst)

            # Make the instance's connections
            for pname, pconn in pinst.connections.items():
                if pname not in inst._resolved.ports:
                    raise RuntimeError(
                        f"Invalid Port {pname} on {inst} in Module {module.name}"
                    )
                # Import the Signal-object
                sig = self.import_connection(pconn, module)
                # And connect it to the Instance
                setattr(inst, pname, sig)

        # Add the Module to our cache and return-namespace, and return it
        self.modules[(pmod.name.domain, pmod.name.name)] = module
        setattr(ns, module.name, module)
        return module

    def import_connection(
        self, pconn: protodefs.Connection, module: Module
    ) -> Union[Signal, Slice, Concat]:
        """ Import a Proto-defined `Connection` into a Signal, Slice, or Concatenation """
        # Connections are a proto `oneof` union; figure out which to import
        stype = pconn.WhichOneof("stype")
        # Concatenations are more complicated and need their own method
        if stype == "concat":
            return self.import_concat(pconn.concat, module)
        # For signals & slices, first sort out the signal-name, so we can grab the object from `module.namespace`
        if stype == "sig":
            sname = pconn.sig.name
        elif stype == "slice":
            sname = pconn.slice.signal
        else:
            raise ValueError(f"Invalid Connection Type: {pconn}")
        # Grab this Signal, if it exists
        sig = module.namespace.get(sname, None)
        if sig is None:
            # This block has held, at some points in code-history,
            # the SPICE-style "create nets from thin air" behavior.
            # That's outta here; undeclared signals produce errors instead.
            raise RuntimeError(f"Invalid Signal {sname} in Module {module.name}")
        # Now chop this up if it's a Slice
        if stype == "slice":
            sig = Slice(signal=sig, top=pconn.slice.top, bot=pconn.slice.bot)
        return sig

    def import_concat(self, pconc: protodefs.Concat, module: Module) -> Concat:
        """ Import a (potentially nested) Concatenation """
        parts = []
        for ppart in pconc.parts:
            part = self.import_connection(ppart, module)
            parts.append(part)
        return Concat(*parts)

    def import_instance(self, pinst: protodefs.Instance) -> Instance:
        """ Convert Proto-Instance `pinst` to an `hdl21.Instance`. 
        Requires an available Module-definition to be referenced. 
        Connections are *not* performed inside this method. """

        # Also a small piece of proof that Google hates Python.
        ref = pinst.module
        if ref.WhichOneof("to") != "qn":  # Only `QualifiedName` is valid and supported
            raise ValueError(f"Invalid reference {ref}")

        if ref.qn.domain == "hdl21.primitives":
            # Retrieve the Primitive from `hdl21.primitives`
            prim = getattr(primitives, ref.qn.name, None)
            if not isinstance(prim, Primitive):
                raise RuntimeError(
                    f"Attempt to import invalid `hdl21.primitive` {ref.qn.name}"
                )

            # Import all of its instance parameters
            pdict = {}
            for pname, pparam in pinst.parameters.items():
                pdict[pname] = self.import_parameter(pparam)
            params = prim.Params(**pdict)

            # Call the Primitive with its parameters, creating a PrimitiveCall Instance-target
            target = prim(params)

        elif ref.qn.domain == self.pkg.name:  # Internally-defined Module
            key = (ref.qn.domain, ref.qn.name)
            module = self.modules.get(key, None)
            if module is None:
                raise RuntimeError(f"Invalid undefined Module {key} ")
            if len(pinst.parameters):
                raise RuntimeError(
                    f"Invalid Instance {pinst} with of Module {module} - does not accept Parameters"
                )
            target = module
        else:
            raise ValueError(f"Undefined Module Domain {ref.qn.domain}")

        return Instance(name=pinst.name, of=target)

    def import_parameter(self, pparam: protodefs.Parameter) -> Any:
        ptype = pparam.WhichOneof("value")
        if ptype == "integer":
            return int(pparam.integer)
        if ptype == "double":
            return float(pparam.double)
        if ptype == "string":
            return str(pparam.string)
        raise ValueError

    def import_port_dir(self, pport: protodefs.Port) -> PortDir:
        # Convert between Port-Direction Enumerations
        if pport.direction == protodefs.Port.Direction.INPUT:
            return PortDir.INPUT
        if pport.direction == protodefs.Port.Direction.OUTPUT:
            return PortDir.OUTPUT
        if pport.direction == protodefs.Port.Direction.INOUT:
            return PortDir.INOUT
        if pport.direction == protodefs.Port.Direction.NONE:
            return PortDir.NONE
        raise ValueError

