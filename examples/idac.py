"""
# Nmos Current DAC Example 

Using stacked generic FinFETs. 
Demonstrates a few common tactics and features: 

* Defining `ExternalModule`s for externally-defined devices, e.g. a small PDK
* Using `Instantiable`s *as parameters* to allow generator-callers to fully specify the device
* Using enumerated parameters to allow generator-callers to select from a set of options

Note the generated sub-circuits will generally have names along the lines of `NmosIdac_{long_string}`, 
e.g. `NmosIdac_46b3842dc8718a80a86891e28bc798e5_`. This 32-character hex-string is a hash of the 
parameters. Hdl21 uses such a method when parameters are "compound", i.e. not a simple scalar. 

For parameters with all scalar values, in contrast, Hdl21 names exported modules with a string 
of their parameter values, e.g. NmosIdac_nbits_5.
"""

import sys
from copy import deepcopy
from enum import Enum, auto

import hdl21 as h


@h.paramclass
class FinFetParams:
    """# FinFet Stack Parameters"""

    nfin = h.Param(dtype=h.Scalar, desc="Number of Fins", default=4)
    nf = h.Param(dtype=int, desc="Number of Fingers", default=1)
    m = h.Param(dtype=int, desc="Multiplier", default=1)
    stack = h.Param(dtype=int, desc="Number series stacked", default=1)


# Define two transistor `ExternalModule`s named `n` and `p`
n = h.ExternalModule(
    name="n",
    paramtype=FinFetParams,
    port_list=deepcopy(h.MosPorts),
)
p = h.ExternalModule(
    name="p",
    paramtype=FinFetParams,
    port_list=deepcopy(h.MosPorts),
)


class PdkEnum(Enum):
    """A hypothetical enumeration of supported FinFET PDKs."""

    FAKEFET = auto()  # The only value, for now!


@h.paramclass
class Params:
    """# Nmos Current DAC Parameters"""

    mnsw = h.Param(dtype=h.Instantiable, desc="Nmos Switch Unit")
    mnbi = h.Param(dtype=h.Instantiable, desc="Nmos Bias Unit")
    pdk = h.Param(dtype=PdkEnum, desc="Enumerated Target Technology")
    width = h.Param(dtype=int, desc="DAC Bit Width")


@h.generator
def NmosIdac(params: Params) -> h.Module:
    """# Nmos Current DAC Generator"""

    @h.module
    class Unit:
        """# NMOS DAC Unit Cell
        * Bias transistor instance of `mnbi`
        * Switch transistor instance of `mnsw`
        """

        d, g, en, VSS = 4 * h.Port()
        nsw = params.mnsw(d=d, g=en, b=VSS)
        nbi = params.mnbi(d=nsw.s, g=g, s=VSS, b=VSS)

    @h.module
    class NmosIdac:
        """# Nmos Current DAC"""

        # IO Interface
        iin = h.Input(desc="Input Bias Current")
        out = h.Output(desc="Output Current")
        code = h.Input(width=params.width, desc="DAC Control Code. Parametric Width.")
        hi = h.Input(desc="Logic High")
        VSS = h.Input(usage=h.Usage.GROUND)

        # Create the diode-connected input device
        uin = Unit(d=iin, g=iin, en=hi, VSS=VSS)

    # Create the primary output units
    for c in range(params.width):
        unit = (2**c) * Unit(
            d=NmosIdac.out,  #
            g=NmosIdac.iin,
            en=NmosIdac.code[c],
            VSS=NmosIdac.VSS,
        )
        NmosIdac.add(unit, name=f"unit{c}")

    return NmosIdac


def main():
    """# Main Entry Point
    Create an instance of our `NmosIdac`."""

    # Create a set of parameters
    params = Params(
        mnsw=n(nfin=4, nf=2, m=1, stack=1),
        mnbi=n(nfin=4, nf=1, m=2, stack=12),
        width=3,
        pdk=PdkEnum.FAKEFET,
    )

    # Run the generator function
    dut = NmosIdac(params)

    # And print a SPICE netlist of it
    h.netlist(dut, sys.stdout, fmt="spice")


if __name__ == "__main__":
    main()
