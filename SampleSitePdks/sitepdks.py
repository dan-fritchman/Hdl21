"""
# Sample Site-Specific PDK Installation(s)

Create the `hdl21.PdkInstall`(s) which load these locations into `hdl21` PDKs. 

This sample module is designed to illustrate setting up a "site's-worth" of such PDK data, 
which generally consists of external files for device models, netlists and the like.  
*This module is a template, designed to be modified and not to work*.  

Usage typically consists of: 

* Import each PDK package
* Create an instance of its `Install` class. 
* Assign that instance to the PDK package's `install` (lower-case) field. 

Each `Install` class is a runtime type-checked `@dataclass`. 
Reviewing its members and their types should serves as sound documentation of 
what is required, valid, and how the fields relate. 

The two examples used here are PDK packages built into the Hdl21 source tree: 
the ASAP7 academic predictive kit, and the Skywater 130nm open-source PDK. 

"""

from pathlib import Path
import os

# Sky 130
import sky130_hdl21

sky130_hdl21.install = sky130_hdl21.Install(
    pdk_path=Path(os.environ["PDK_ROOT"] + "/" + os.environ["PDK"]),
    lib_path=Path("libs.tech/ngspice/sky130.lib.spice"),
    model_ref=Path("libs.ref/sky130_fd_pr/spice"),
)

# ASAP7
import asap7_hdl21

# FIXME: Complete implementation
# asap7_hdl21.install = asap7_hdl21.Install(Path("pdks") / "asap7" / "..." / "7nm_TT.pm")

# GF180
import gf180_hdl21

gf180_hdl21.install = gf180_hdl21.Install(
    model_lib=Path("/usr/local/share/pdk/gf180mcuC/libs.tech/ngspice/sm141064.ngspice")
)
