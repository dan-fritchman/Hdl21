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

# Sky 130
import sky130

sky130.install = sky130.Install(
    model_lib=Path("pdks") / "sky130" / ... / "sky130.lib.spice"
)

# ASAP7
import asap7

asap7.install = asap7.Install(
    model_lib=Path("pdks") / "asap7" / ... / "7nm_TT.pm"
)

