""" 
# Hdl21 Netlisting 
"""

from typing import IO, Union, Optional

# Import the core netlisting from `vlsirtools`
import vlsir
from vlsirtools.netlist import (
    netlist as vlisr_netlist,
    NetlistFormat,
    NetlistFormatSpec,
    NetlistOptions,
)

from .elab import Elaboratables
from .proto.to_proto import to_proto


def netlist(
    src: Union[Elaboratables, vlsir.circuit.Package],
    dest: IO,
    *,
    domain: Optional[str] = None,
    **kwargs
) -> None:
    """
    # Hdl21 Netlisting

    Netlist one or more Hdl21 `Elaboratable`s - typically `Module`s - or a VLSIR `Package` to destination `dest`.
    All other options are forwarded to the underlying VLSIR netlister.

    Example usages:
    ```python
    h.netlist(MyModule, dest=open('mynetlist.v', 'w'), fmt='verilog')
    ```
    ```python
    s = StringIO()
    h.netlist(MyGenerator(Params()), dest=s, fmt='spectre')
    ```
    ```python
    import sys
    h.netlist(h.to_proto([MyModule, MyGenerator(Params())]), dest=sys.stdout, fmt='spice')
    ```
    """

    # Convert to the Vlsir `Package` if necessary
    if not isinstance(src, vlsir.circuit.Package):
        pkg = to_proto(top=src, domain=domain)
    else:
        pkg = src

    # And invoke the VLSIR netlister
    return vlisr_netlist(pkg=pkg, dest=dest, **kwargs)
