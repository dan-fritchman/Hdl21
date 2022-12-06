"""
# Mark each Module as elaborated
"""

# Local imports
from ...module import Module
from .base import Elaborator


class MarkModules(Elaborator):
    def elaborate_module(self, module: Module) -> Module:
        # Seriously. That's it.
        module._elaborated = module
        # `_elaborated` is the module itself,
        # and not just a boolean, in case we want to
        # have differences between the two some day.
