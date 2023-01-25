"""
# Mark each Module as elaborated
"""

# Local imports
from ...module import Module
from .base import Elaborator


class MarkModules(Elaborator):
    def elaborate_module(self, module: Module) -> Module:
        # Check that every module has a name
        if not module.name:
            msg = f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            self.fail(msg)

        # `_elaborated` is the module itself,
        # and not just a boolean, in case we want to
        # have differences between the two some day.
        module._elaborated = module
