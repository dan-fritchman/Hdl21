from typing import Union, Sequence, TypeVar

# Shorthand type alias for "an element or list thereof", used by all the call signatures below
T = TypeVar("T")
OneOrMore = Union[T, Sequence[T]]
