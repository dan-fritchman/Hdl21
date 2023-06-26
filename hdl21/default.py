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

    def __new__(cls, *_, **__):
        # And we're a singleton. Call away, you get the same class-object back.
        return Default
