"""
# External Schematic Module

Wrapper for circuits defined in a schematic outside Hdl21. 
"""

from pydantic.dataclasses import dataclass
from pathlib import Path

# Local imports
from .external_module import ExternalModule
from .qualname import qualname_magic_methods

@dataclass
@qualname_magic_methods
class SchematicModule(ExternalModule):
    """
    # External Schematic Module

    Wrapper for circuits defined in a schematic outside Hdl21

    name property is the netlist subckt name

    """
    schematic_filepath: Path