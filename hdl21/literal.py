from pydantic.dataclasses import dataclass


@dataclass
class Literal:
    """
    # Literal
    A thin wrapper around a string, generally to be used outside Hdl21, e.g. in external netlists.
    """

    content: str
