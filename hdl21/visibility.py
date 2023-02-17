"""
# Visibility 

Annotations for HDL objects to be visible inside or outside their parent, generally Module. 
Prominent examples include the annotations of which `Signal`s are exposed as ports. 
"""

from enum import Enum


class Visibility(Enum):
    """# Visibility Enumeration"""

    INTERNAL = "INTERNAL"  # Internal/ private
    PORT = "PORT"  # Exposed as a Port
