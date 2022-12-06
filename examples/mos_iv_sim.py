"""
# Mos DC Simulation 

A simple, common spice-class simulation example, 
sweeping the gate voltage of an Nmos transistor
from the built-in sample PDK.
"""

import hdl21 as h
import hdl21.sim as hs
from hdl21.prefix import m
import vlsirtools.spice as vsp

# Import the built-in sample PDK
from hdl21.pdk import sample_pdk


@h.module
class MosIvTb:
    """Mos I-V Sweep Testbench"""

    VSS = h.Port()  # The testbench interface: sole port VSS

    mos = sample_pdk.Nmos()(s=VSS, b=VSS)  # The transistor under test
    vd = h.Vdc(dc=1800 * m)(p=mos.d, n=VSS)
    vg = h.Vdc(dc="vgs")(p=mos.g, n=VSS)


@hs.sim
class MosIvSim:
    """Mos I-V Sweep Simulation Input"""

    tb = MosIvTb  # Set our testbench
    vgs = hs.Param(val=1800 * m)  # Sweep parameter VGS
    dc = hs.Dc(var=vgs, sweep=hs.LinearSweep(start=0, stop=1800 * m, step=10 * m))
    mod = hs.Include(sample_pdk.install.models)


def main():
    """Run the `MosIvSim` simulation, and print its results"""

    # First check which simulators are available.
    # DC parameter sweeps such as this one are supported by Xyce and Spectre.
    if not vsp.xyce.available() and not vsp.spectre.available():
        print("No supported simulators available. Skipping simulation.")
        return

    # Run the simulation!
    results = MosIvSim.run()
    # And print the results to the console
    print(results)


if __name__ == "__main__":
    main()
