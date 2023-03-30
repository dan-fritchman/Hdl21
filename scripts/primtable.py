"""
# Primitive Table Generation 

Writes the markdown-format table of primitives used in documentation.
"""

# import sys
# from typing import IO
from pydantic.dataclasses import dataclass
from hdl21.primitives import _primitives, PrimLibEntry


@dataclass
class Widths:
    name: int
    desc: int
    prim_type: int
    aliases: int
    port_list: int


@dataclass
class Row:
    name: str
    desc: str
    prim_type: str
    aliases: str
    port_list: str

    def fmt(self, widths: Widths) -> str:
        """Format a row of the table to `widths`."""
        name = self.name.ljust(widths.name)
        desc = self.desc.ljust(widths.desc)
        prim_type = self.prim_type.ljust(widths.prim_type)
        aliases = self.aliases.ljust(widths.aliases)
        port_list = self.port_list.ljust(widths.port_list)
        return f"| {name} | {desc} | {prim_type} | {aliases} | {port_list} |"


def row(entry: PrimLibEntry) -> Row:
    """Get a `Row` for a primitive library entry."""
    prim = entry.prim
    aliases = entry.aliases
    return Row(
        name=prim.name,
        desc=prim.desc,
        prim_type=prim.primtype.name,
        aliases=", ".join(aliases),
        port_list=", ".join([p.name for p in prim.port_list]),
    )


def table():
    print("\n\n\n Generating Primitive Table \n\n\n")

    # Collect up a `Row` for each primitive.
    rows = [row(entry) for entry in _primitives.values()]

    # Calculate column widths
    widths = Widths(
        name=max(len(row.name) for row in rows),
        desc=max(len(row.desc) for row in rows),
        prim_type=max(len(row.prim_type) for row in rows),
        aliases=max(len(row.aliases) for row in rows),
        port_list=max(len(row.port_list) for row in rows),
    )

    # Create the header row and markdown-formatted separator.
    header = Row(
        name="Name",
        desc="Description",
        prim_type="Type",
        aliases="Aliases",
        port_list="Ports",
    )
    separator = Row(
        name="-" * widths.name,
        desc="-" * widths.desc,
        prim_type="-" * widths.prim_type,
        aliases="-" * widths.aliases,
        port_list="-" * widths.port_list,
    )

    # Get around to formatting and writing the table
    print(header.fmt(widths))
    print(separator.fmt(widths))
    for r in rows:
        print(r.fmt(widths))


table()
