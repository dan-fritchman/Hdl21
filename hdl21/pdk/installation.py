"""
# PDK Installations 

In addition to their in-memory, Hdl21-representable content, 
process development kits (PDK)s often require large suites of files 
which represent the underlying technology. 

Transistor models and SPICE "library" files are common examples 
pertinent to Hdl21. Tech-files, layout libraries, and the like 
are similarly necessary for related pieces of software. 

Each `hdl21.pdk.PdkInstallation` represents a typical *site installation*, 
i.e. the combination of that content and its location on a 
particular file system. 

Tracking such site-specific content through long call-stacks 
can be pedantic, especially since the information is generally 
shared throughout a python process. The typical usage to avoid this is to, 
in a "site-specific" module or package, 

* Import the target PDK module 
* Create an instance of its `PdkInstallation` subtype
* Affix that instance to the PDK module's `install` member 

E.g. 
```python
# "sitepdks.py", or similar

import mypdk 

mypdk.install = mypdk.Install(
    models = "/path/to/models",
    path2 = "/path/2",
    # etc.
)
```

Any programs needing the site-specific data can then import `mysite`, 
while code directly requiring the contents of the `PdkInstall` need 
not be directly aware of its contents. 
For example when invoking a simulation requiring `mypdk`'s models:

```python 
# Simulation Invocation 
# Presumes `mysite` or similar has set `mypdk.install` beforehand. 

import mypdk
sim = Sim(tb=tb)
sim.lib(mypdk.install.models, "ss")
sim.run()
```

"""

from pydantic.dataclasses import dataclass


@dataclass
class PdkInstallation:
    """
    # PDK Installation

    A named set of PDK-related data, typically including details of
    a particular "site installation" of external files and settings.

    While often comprised of file-system `Path`s, the content of a `PdkInstallation`
    can in principle be anything related to the installation,
    e.g. compilation settings for a particular tool, or metadata indicating
    relevant tool versions.

    Most PDK modules should generally create a `pydantic.dataclass` which is also
    a sub-class of `PdkInstallation`, e.g.

    ```python
    # mypdk.py

    from pathlib import Path
    from pydantic.dataclasses import dataclass
    from hdl21.pdk import PdkInstallation

    @dataclass
    class Install(PdkInstallation):
        model_file: Path
        options: Dict[str, str]
    ```

    ```python
    # site.py
    import mypdk

    mypdk.install = mypdk.Install(
        model_file = "/my/pdk/models",
        options = {"opt" : "max"}
    )
    ```

    ```python
    # Application-Level Code
    # Running an example simulation with `mypdk`

    import site   # Creates the site-specific `PdkInstallation`s
    import mypdk  # Import the target PDK

    sim = Sim(tb=tb)
    sim.lib(mypdk.install.models, "ss")
    sim.run()
    ```

    This "installation data" can in principle be store anywhere, or in unstructured types.
    The primary goal of the `PdkInstallation` type is to centralize this data,
    and to enable shorthand registration and recall, particularly for
    the common case of a single in-memory `PdkInstallation`.
    """

    ...  # No content
