"""
# Default Value Sentinel 

Used by a number of Hdl21 types to indicate a default value, 
where all other "public" values could be valid non-default data. 
"""

from .datatype import datatype


@datatype
class Default:
    """
    # Default Value Sentinel

    Used by a number of Hdl21 types to indicate a default value,
    where all other "public" values could be valid non-default data.
    """

    ...  # Empty contents
