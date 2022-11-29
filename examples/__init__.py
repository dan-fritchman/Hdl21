"""
# Examples "Package"
## `__init__.py`, the file that makes it a package (and does nothing else).

This `examples/` folder isn't really designed to be used as a package, 
but we derive plenty of benefit from `pytest`ing it, and moreover 
from its test module being able to make relative imports like 

```python
from .ro import main # Only works in a package
```

Each `example` is *written* to be run as a script. 
This shouldn't stop them from being run as such, 
although it's always worth worrying about Python's demands for differences 
between scripts and library modules, especially inasmuch as `import`s are concerned.
"""
