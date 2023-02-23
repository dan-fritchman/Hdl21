"""
hdl21 ProtoBuf Import 
"""
from types import SimpleNamespace
from typing import Union, Any, Dict, List, Optional

# Local imports
# Proto-definitions
import vlsir
import vlsir.circuit_pb2 as vckt

# HDL
from ..prefix import Prefix, Prefixed
from ..module import Module
from ..external_module import ExternalModule
from ..instance import Instance
from ..signal import Signal, PortDir, Visibility
from ..slice import Slice
from ..concat import Concat
from .. import primitives
from ..primitives import Primitive, Vpulse


def from_proto(pkg: vckt.Package) -> SimpleNamespace:
    """Convert Proto-defined Package `pkg` to a namespace-full of Modules."""
    importer = ProtoImporter(pkg)
    return importer.import_()


class ProtoImporter:
    """Protobuf Package Importer.
    Collects all `Modules` defined in Protobuf-sourced primary-argument `pkg` into a Python `types.SimpleNamespace`."""

    def __init__(self, pkg: vckt.Package):
        self.pkg = pkg
        self.modules = dict()  # Dict of names to Modules
        self.ext_modules = dict()  # Dict of qual-names to ExternalModules
        self.ns = SimpleNamespace()
        self.ns.name = pkg.domain

    def import_(self) -> SimpleNamespace:
        """Import the top-level `Package` to a Python namespace"""
        # Walk through each proto-defined Module
        # External modules first, as we know they have no dependencies
        for emod in self.pkg.ext_modules:
            self.import_external_module(emod)
        for pmod in self.pkg.modules:
            self.import_module(pmod)
        # Return our collected namespace
        return self.ns

    def get_namespace(self, path: List[str]) -> SimpleNamespace:
        """Get a (potentially nested) namespace at `path`, creating levels along the way if necessary ."""
        ns = self.ns
        for part in path:
            attr = getattr(ns, part, None)
            if attr is None:  # Create a new Namespce
                new_ns = SimpleNamespace()
                new_ns.name = part
                setattr(ns, part, new_ns)
                ns = new_ns
            elif isinstance(attr, SimpleNamespace):
                ns = attr
            else:
                raise RuntimeError(f"Invalid namespace path {path} overwriting {attr}")
        return ns

    def import_external_module(self, pmod: vckt.ExternalModule) -> ExternalModule:
        """Convert Proto-Module `emod` to an `hdl21.ExternalModule`"""

        # Check our cache for whether a module by the same name has been imported
        key = (pmod.name.domain, pmod.name.name)
        if key in self.ext_modules:
            conflict = self.ext_modules[key]
            msg = f"Cannot import conflicting definitions of {pmod} and {conflict}"
            raise RuntimeError(msg)

        # Import the port list
        port_list = import_ports_and_signals(pmod)

        # Create the ExternalModule
        emod = ExternalModule(
            name=pmod.name.name,
            domain=pmod.name.domain,
            desc=pmod.desc,
            port_list=port_list,
            paramtype=dict,  # FIXME: should these be stored in the serialization schema?
        )
        # Give it a (non-initializer) value for its `importpath`
        emod._importpath = [pmod.name.domain]
        # Cache and return it
        self.ext_modules[key] = emod
        return emod

    def import_module(self, pmod: vckt.Module) -> Module:
        """Convert Proto-Module `pmod` to an `hdl21.Module`"""
        if pmod.name in self.modules:
            raise RuntimeError(f"Proto Import Error: Redefined Module {pmod.name}")

        # Create the Module
        module = Module()
        # Get or create its namespace, and set its name
        path = pmod.name.split(".")  # Path-parts are dot-separated
        ns = self.get_namespace(path[:-1])
        # Save the import-path and name
        module._importpath = path[:-1]
        module.name = path[-1]

        # Import its signals and ports
        for sig in import_ports_and_signals(pmod):
            module.add(sig)

        # Lap through instances, connecting them, creating internal Signals if necessary (bleh)
        for pinst in pmod.instances:
            inst = self.import_instance(pinst)
            module.add(inst)

            # Make the instance's connections
            for pconn in pinst.connections:
                if pconn.portname not in inst._resolved.ports:
                    msg = f"Invalid Port {pconn.portname} on {inst} in Module {module.name}"
                    raise RuntimeError(msg)
                # Import the Signal-object
                conn = import_connection_target(pconn.target, module)
                # And connect it to the Instance
                inst.connect(pconn.portname, conn)

        # Add the Module to our cache and return-namespace, and return it
        self.modules[pmod.name] = module
        setattr(ns, module.name, module)
        return module

    def import_instance(self, pinst: vckt.Instance) -> Instance:
        """Convert Proto-Instance `pinst` to an `hdl21.Instance`.
        Requires an available Module-definition to be referenced.
        Connections are *not* performed inside this method."""

        # Also a small piece of proof that Google hates Python.
        ref = pinst.module
        if ref.WhichOneof("to") == "local":
            # Internally-defined Module
            module = self.modules.get(ref.local, None)
            if module is None:
                raise RuntimeError(f"Invalid undefined Module {ref.local} ")
            if len(pinst.parameters):
                msg = f"Invalid Instance {pinst} with of Module {module} - does not accept Parameters"
                raise RuntimeError(msg)
            target = module

        elif ref.WhichOneof("to") == "external":  # Defined outside package
            # Import all of its instance parameters to a dict
            params = import_parameters(pinst.parameters)

            # First check the priviledged/ internally-defined domains
            if ref.external.domain == "vlsir.primitives":
                # Import a VLSIR primitive to an ideal element, and convert its parameters
                target = import_vlsir_primitive(ref.external)
                remapped_params = import_primitive_params(target, params)
                params = target.Params(**remapped_params)

            elif ref.external.domain in (
                "hdl21.primitives",
                "hdl21.ideal",
            ):
                # Retrieve the Primitive from `hdl21.primitives`, and convert its parameters
                target = import_hdl21_primitive(ref.external)
                params = target.Params(**params)

            else:  # Externally-defined `ExternalModule`
                # These must be declared in our `Package` being imported. Look up its header-info from `ext_modules`.
                key = (ref.external.domain, ref.external.name)
                target = self.ext_modules.get(key, None)
                if target is None:
                    msg = f"Invalid Instance of undefined External Module {key}"
                    raise RuntimeError(msg)

            # Call the `target` ExternalModule/ Primitive it with the parameters, making an instantiable `Call`-object.
            target = target(params)

        else:
            raise ValueError

        return Instance(name=pinst.name, of=target)


def import_ports_and_signals(
    pmod: Union[vckt.Module, vckt.ExternalModule]
) -> List[Signal]:
    """Import all Ports and Signals from Proto-Module `pmod`.
    Returns them as a single list, which can serve as arguments to `Module.add` or `ExternalModule.port_list`."""

    # Keep a dictionary from name: Signal imported
    signals: Dict[str, Signal] = {}
    for psig in pmod.signals:
        signals[psig.name] = Signal(name=psig.name, width=psig.width)

    # Convert the entries of `signals` that are ports
    for pport in pmod.ports:
        dir_ = import_port_dir(pport)
        if pport.signal not in signals:
            msg = f"Port {pport} missing Signal in {signals}"
            raise RuntimeError(msg)
        signals[pport.signal].direction = dir_
        signals[pport.signal].vis = Visibility.PORT

    return list(signals.values())


def import_hdl21_primitive(pref: vlsir.utils.QualifiedName) -> Primitive:
    """Convert an `hdl21.primitives` or `hdl21.ideal` qualified name to a Primitive."""
    if pref.domain not in ["hdl21.primitives", "hdl21.ideal"]:
        raise ValueError(f"Invalid Primitive Domain: {pref.domain}")

    # Get the Primitive from `hdl21.primitives`, or fail
    prim = getattr(primitives, pref.name, None)
    if not isinstance(prim, Primitive):
        msg = f"Attempt to import invalid `hdl21.primitive` {pref.external.name}"
        raise RuntimeError(msg)
    return prim


def import_vlsir_primitive(pref: vlsir.utils.QualifiedName) -> Primitive:
    """Import a VLSIR-defined Primitive"""
    if pref.domain != "vlsir.primitives":
        raise ValueError(f"Invalid Primitive Domain: {pref.domain}")

    # Mapping from `vlsir.primitives` to Hdl21's ideal elements
    # FIXME: specialized importing of their parameters!
    prim_map = {
        "vdc": "DcVoltageSource",
        "vpulse": "PulseVoltageSource",
        "vsin": "SineVoltageSource",
        "isource": "CurrentSource",
        "resistor": "IdealResistor",
        "capacitor": "IdealCapacitor",
        "inductor": "IdealInductor",
        "vcvs": "VoltageControlledVoltageSource",
        "vccs": "VoltageControlledCurrentSource",
        "ccvs": "CurrentControlledVoltageSource",
        "cccs": "CurrentControlledCurrentSource",
    }
    if pref.name not in prim_map:
        msg = f"Invalid or unsupported VLSIR Primitive: {pref.name}"
        raise RuntimeError(msg)

    # Get the Hdl21 Primitive class
    prim = getattr(primitives, prim_map[pref.name], None)
    if not isinstance(prim, Primitive):
        msg = f"Attempt to import invalid `hdl21.primitive` {pref.external.name}"
        raise RuntimeError(msg)
    return prim


def import_parameters(pparams: List[vlsir.Param]) -> Dict[str, Any]:
    """Import a list of Vlsir parameters to a Hdl21-style {name: value} dict."""
    return {pparam.name: import_parameter_value(pparam.value) for pparam in pparams}


def import_parameter_value(
    pparam: vlsir.ParamValue,
) -> Union[int, float, str, Prefixed]:
    """Import a `ParamValue`"""
    ptype = pparam.WhichOneof("value")
    if ptype == "integer":
        return int(pparam.integer)
    if ptype == "double":
        return float(pparam.double)
    if ptype == "string":
        return str(pparam.string)
    if ptype == "literal":
        return str(pparam.literal)
    if ptype == "prefixed":
        return import_prefixed(pparam.prefixed)
    raise ValueError(f"Invalid Parameter Type: `{ptype}`")


def import_connection_target(
    pconn: vckt.ConnectionTarget, module: Module
) -> Union[Signal, Slice, Concat]:
    """Import a Proto-defined `ConnectionTarget` into a Signal, Slice, or Concatenation"""
    # Connections are a proto `oneof` union; figure out which to import
    stype = pconn.WhichOneof("stype")
    # Concatenations are more complicated and need their own method
    if stype == "concat":
        return import_concat(pconn.concat, module)
    # For signals & slices, first sort out the signal-name, so we can grab the object from `module.namespace`
    if stype == "sig":
        sname = pconn.sig
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
        start = pconn.slice.bot
        stop = pconn.slice.top + 1  # Move to Python-style exclusive indexing
        sig = Slice(parent=sig, index=slice(start, stop))
    return sig


def import_concat(pconc: vckt.Concat, module: Module) -> Concat:
    """Import a (potentially nested) Concatenation"""
    parts = []
    for ppart in pconc.parts:
        part = import_connection_target(ppart, module)
        parts.append(part)
    return Concat(*parts)


def import_port_dir(pport: vckt.Port) -> PortDir:
    """Convert between Port-Direction Enumerations"""
    if pport.direction == vckt.Port.Direction.INPUT:
        return PortDir.INPUT
    if pport.direction == vckt.Port.Direction.OUTPUT:
        return PortDir.OUTPUT
    if pport.direction == vckt.Port.Direction.INOUT:
        return PortDir.INOUT
    if pport.direction == vckt.Port.Direction.NONE:
        return PortDir.NONE
    raise ValueError


def import_prefix(vpre: vlsir.SIPrefix) -> Prefix:
    """Import an enumerated `Prefix`"""
    map = {
        vlsir.SIPrefix.YOCTO: Prefix.YOCTO,
        vlsir.SIPrefix.ZEPTO: Prefix.ZEPTO,
        vlsir.SIPrefix.ATTO: Prefix.ATTO,
        vlsir.SIPrefix.FEMTO: Prefix.FEMTO,
        vlsir.SIPrefix.PICO: Prefix.PICO,
        vlsir.SIPrefix.NANO: Prefix.NANO,
        vlsir.SIPrefix.MICRO: Prefix.MICRO,
        vlsir.SIPrefix.MILLI: Prefix.MILLI,
        vlsir.SIPrefix.CENTI: Prefix.CENTI,
        vlsir.SIPrefix.DECI: Prefix.DECI,
        vlsir.SIPrefix.DECA: Prefix.DECA,
        vlsir.SIPrefix.HECTO: Prefix.HECTO,
        vlsir.SIPrefix.KILO: Prefix.KILO,
        vlsir.SIPrefix.MEGA: Prefix.MEGA,
        vlsir.SIPrefix.GIGA: Prefix.GIGA,
        vlsir.SIPrefix.TERA: Prefix.TERA,
        vlsir.SIPrefix.PETA: Prefix.PETA,
        vlsir.SIPrefix.EXA: Prefix.EXA,
        vlsir.SIPrefix.ZETTA: Prefix.ZETTA,
        vlsir.SIPrefix.YOTTA: Prefix.YOTTA,
        vlsir.SIPrefix.UNIT: Prefix.UNIT,  # Welcome to the party, as of version 2.0!
    }
    if vpre not in map:
        raise ValueError(f"Invalid Prefix {vpre}")
    return map[vpre]


def import_prefixed(vpref: vlsir.Prefixed) -> Prefixed:
    """Import a `Prefixed` number"""

    # Import the metric prefix
    prefix = import_prefix(vpref.prefix)

    # And import the numeric part, dispatched across its type.
    ptype = vpref.WhichOneof("number")
    if ptype == "integer":
        number = vpref.integer
    elif ptype == "double":
        number = vpref.double
    elif ptype == "string":
        number = vpref.string
    else:
        raise ValueError(f"Invalid Parameter Type: `{ptype}`")

    return Prefixed(number=number, prefix=prefix)


def import_primitive_params(
    target: Primitive, params: Any
) -> Dict[str, Optional[Prefixed]]:
    """Convert the parameters of an `IDEAL` VLSIR element into a primtive form.
    Returns the result as a dictionary of {name: value}s."""

    if target is Vpulse:
        return dict(
            v1=params["v1"],
            v2=params["v2"],
            delay=params["td"],
            rise=params["tr"],
            fall=params["tf"],
            width=params["tpw"],
            period=params["tper"],
        )

    return params
