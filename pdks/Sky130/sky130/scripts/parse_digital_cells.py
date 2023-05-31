def parse_spice_file(file_path, library):
    logic_modules = []

    acronym = "".join([l[0] for l in library.split()])

    logic_modules.append(acronym + " : Dict[str : h.ExternalModule] = {")

    with open(file_path, "r") as f:
        for line in f:
            if line.startswith(".subckt"):
                # Remove '.subckt' and split the line into words
                elements = line[7:].split()

                modname = elements[0]
                # Get the port list
                ports = elements[1:]

                # Create the logic module string
                logic_module = (
                    f'\t "{modname}" : _logic_module("{modname}","{library}",{ports}),'
                )
                logic_modules.append(logic_module)

    logic_modules.append("}")

    return logic_modules


def write_parser_file(logic_modules, output_file):
    with open(output_file, "w") as f:
        for module in logic_modules:
            f.write(module + "\n")


# Example usage:
modules = parse_spice_file("sky130_fd_sc_ls.spice", "Low Speed")
write_parser_file(modules, "fd_sc_ls.py")
