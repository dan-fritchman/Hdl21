def parse_spice_file(file_path):
    logic_modules = []

    name = file_path.split(".")[0]

    logic_modules.append(name + " : Dict[str, h.ExternalModule] = {")

    with open(file_path, "r") as f:
        for line in f:
            if line.startswith(".SUBCKT"):
                # Remove '.subckt' and split the line into words
                elements = line[7:].split()

                modname = elements[0].split(name + "__")[-1]
                # Get the port list
                ports = elements[1:]

                # Create the logic module string
                logic_module = (
                    f'\t "{modname}" : logic_module("{modname}","{name}",{ports}),'
                )
                logic_modules.append(logic_module)

    logic_modules.append("}")

    return logic_modules


def write_parser_file(logic_modules, output_file):
    with open(output_file, "w") as f:
        for module in logic_modules:
            f.write(module + "\n")


# Example usage:
modules = parse_spice_file("gf180mcu_fd_sc_mcu9t5v0.spice")
write_parser_file(modules, "sc_mcu9t5v0.py")
