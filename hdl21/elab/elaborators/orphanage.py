"""
# Orphan-Testing (Orphanage) Elaborator
"""

# Local imports
from ...module import Module, ModuleAttr
from ...instance import _Instance

# Import the base class
from .base import Elaborator


class Orphanage(Elaborator):
    """# Orphan-Checking Elaborator Pass

    Ensures each Module-attribute is "parented" by the `Module` which holds it.
    Errant cases can come up for code such as:

    ```
    m1 = h.Module(name='m1')
    m1.s = h.Signal() # Signal `s` is now "parented" by `m1`

    m2 = h.Module(name='m2')
    m2.y = m1.s # Now `s` has been "orphaned" (or perhaps "cradle-robbed") by `m2`
    ```

    This essentially boils down to the difference between Python's native reference-semantics,
    and `hdl21.Module`'s notion of "owning" its attributes.
    Note other *references* to Module attributes are allowed, such as:

    ```
    m1 = h.Module(name='m1')
    m1.s = h.Signal() # Signal `s` is now "parented" by `m1`

    my_favorite_signals = { "from_m1" : m1.s }
    ```

    Here the dictionary `my_favorite_signals` retains a reference to Signal `s`.
    This does not generate an orphan-error complaint, so long as `Module`-parent is unique and unambiguous.

    The orphan-test is very simple: each Module-attribute is annotated with a `_parent_module` member
    upon insertion into the Module namespace.
    Orphan-testing simply requires that for each attribute, this member is identical to the parent Module.
    A `RuntimeError` is raised if orphaned attributes are detected.
    Otherwise each Module is returned unchanged.
    """

    def elaborate_module(self, module: Module) -> Module:
        """Elaborate a Module"""

        # Check each attribute in the module namespace for orphanage.
        for attr in module.namespace.values():
            self.assert_parentage(module, attr)

        # Check instance connections, which are not in the module namespace.
        instlike = (
            list(module.instances.values())
            + list(module.instarrays.values())
            + list(module.instbundles.values())
        )
        for inst in instlike:
            self.check_instance(module, inst)

        # Checks out! Return the module unchanged.
        return module

    def check_instance(self, module: Module, inst: _Instance) -> None:
        """Check the connections of `inst` in parent `module`"""
        self.stack.append(inst)

        # Check each of the instance's connections
        for conn in inst.conns.values():
            self.check_connectable(module, conn)

        self.stack.pop()

    def check_connectable(self, module: Module, conn: "Connectable") -> None:
        """Check a Connectable for orphanage.
        Dispatches across connectable types, and recursively follows `conn` back to its constituent and/or parent elements."""

        from ... import (
            NoConn,
            Signal,
            Slice,
            Concat,
            BundleInstance,
            BundleRef,
            AnonymousBundle,
            PortRef,
        )

        # Check owned types first: Signals and Bundle Instances
        if isinstance(conn, (Signal, BundleInstance)):
            return self.assert_parentage(module, conn)

        if isinstance(conn, Slice):
            # Recursively check the parent-signals of slices
            return self.check_connectable(module, conn.parent)

        if isinstance(conn, Concat):
            # Check each of the concatenated signals, also recursively across inner types
            for part in conn.parts:
                self.check_connectable(module, part)
            return

        if isinstance(conn, NoConn):
            # `NoConn`s are not "parented" by anything; they are essentially exempt from this check.
            return

        if isinstance(conn, PortRef):
            # For Port references, check that `module` owns their target Instance
            return self.assert_parentage(module, conn.inst)

        if isinstance(conn, BundleRef):
            # For Bundle references, check that `module` owns their root Bundle Instance
            return self.assert_parentage(module, conn.root())

        if isinstance(conn, AnonymousBundle):
            for sig in conn._namespace.values():
                self.check_connectable(module, sig)
            return

        raise TypeError(f"Orphanage: Unhandled Connectable `{conn}`")

    def assert_parentage(self, module: Module, attr: ModuleAttr) -> None:
        """Assert that `attr` is parented by `module`, or fail."""

        if attr._parent_module is None:
            msg = f"Orphanage! Module `{module.name}` depends on orphan attribute `{attr}`! "
            msg += "Did you forget to `add()` or assign it into `{module.name}`? "
            self.fail(msg)

        if attr._parent_module is not module:
            msg = f"Orphanage: Module {module} attribute {attr} is actually owned by another Module {attr._parent_module}!"
            self.fail(msg)
