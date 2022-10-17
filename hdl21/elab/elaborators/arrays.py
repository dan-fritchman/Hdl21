"""
# Array Flattening 
"""

# Local imports
from ...module import Module
from ...instance import Instance
from ...portref import PortRef
from ...bundle import BundleInstance
from ...signal import Signal
from ...slice import Slice
from ...concat import Concat

# Import the base class
from .base import Elaborator


class ArrayFlattener(Elaborator):
    """
    Elaboration Pass to Flatten `InstanceArray`s into `Instance`s, broadcast and remake their connections.
    """

    def elaborate_module(self, module: Module) -> Module:
        """Elaborate Module `module`.
        Primarily performs flattening of Instance Arrays, and re-connecting to the resultant flattened instances."""

        # Flatten Instance arrays
        while module.instarrays:
            name, array = module.instarrays.popitem()
            self.stack.append(array)
            module.namespace.pop(name)

            # Visit the array's target
            target = self.elaborate_instance_base(array)

            # And do the real work: flattening it.
            if array.n < 1:
                self.fail(f"Invalid InstanceArray {array} with size {array.n}")

            # Create the new, flat Instances
            new_insts = []
            for k in range(array.n):
                name = self.flatname(
                    segments=[array.name, str(k)], avoid=module.namespace
                )
                inst = module.add(Instance(of=target, name=name))
                new_insts.append(inst)

            # And connect them
            for portname, conn in array.conns.items():
                if isinstance(conn, BundleInstance):
                    # All new instances get the same BundleInstance
                    for inst in new_insts:
                        inst.connect(portname, conn)
                elif isinstance(conn, (Signal, Slice, Concat)):
                    # Get the target-module port, particularly for its width
                    port = target.ports.get(portname, None)
                    if port is None:
                        msg = f"Connection to invalid Port `{portname}` on InstanceArray `{array}` in Module `{module.name}`"
                        self.fail(msg)
                    if not isinstance(port, Signal):
                        msg = f"Invalid Port `{portname}` ({port}) on InstanceArray `{array}` in Module `{module.name}`"
                        self.fail(msg)

                    if port.width == conn.width:
                        # All new instances get the same signal
                        for inst in new_insts:
                            inst.connect(portname, conn)
                    elif port.width * array.n == conn.width:
                        # Each new instance gets a slice, equal to its own width
                        for k, inst in enumerate(new_insts):
                            slize = conn[k * port.width : (k + 1) * port.width]
                            if slize.width != port.width:
                                msg = f"Width mismatch connecting {slize} to {port}"
                                self.fail(msg)
                            inst.connect(portname, slize)
                    else:  # All other width-values are invalid
                        msg = f"Invalid connection of {conn} of width {conn.width} to port {portname} on Array {array.name} of width {port.width}. "
                        msg += f"Valid widths are either {port.width} (broadcasting across instances) and {port.width * array.n} (individually wiring to each)."
                        self.fail(msg)
                elif isinstance(conn, PortRef):
                    msg = f"Error elaborating {array} in {module}. "
                    msg += f"Connection {conn} has not been resolved to a `Signal`. "
                    raise RuntimeError
                else:
                    msg = f"Invalid connection to {conn} in InstanceArray {array}"
                    self.fail(msg)
            self.stack.pop()

        return module
