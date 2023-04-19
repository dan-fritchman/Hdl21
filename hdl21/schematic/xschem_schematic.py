import subprocess, os
from pathlib import Path
from typing import Union, Optional
from hdl21.external_module import ExternalModule

optional_path = Optional[Union[Path, str]]


class XschemSchematic:
    #default_root_result_path = Path.home() / "sim_results"
    def __init__(self, path: Union[Path, str], 
                 netlist_dirpath: Union[Path, str]) -> None:
        self.path = Path(path)
        self.netlist_dirpath = Path(netlist_dirpath)
        

    def external_module(self):
        return ExternalModule()

    def netlist(self) -> str:
        """netlist an xschem schematic using the xschem binary.
           Ignores all the options in the xschem directory"""
        self.check_tool_is_available()
        
        print(f"netlisting {str(self.path)}\n to {self.netlist_dirpath}")
        #self.netlist_dirpath.rmdir()
        self.netlist_dirpath.mkdir(parents=True,exist_ok=True)
        options = [
            "-q","-x",
            "-n", "-o", str(self.netlist_dirpath),
            "-l", str(self.netlisting_log_path),
            ]
        command = ["xschem"]
        command.extend(options)
        command.append(str(self.path))
        run_result=subprocess.run(command, capture_output=True, check=True)
        with open(self.netlist_filepath) as netlist_file:
            netlist = netlist_file.read()
        return netlist

    def convert_top_to_lib(self, lib_filepath: optional_path) -> str:
        """
        Updates the top-level netlist to a spice lib file.  This includes
        both the top-level design as  subckt and all the containing subckts.
        If "lib_filepath" is specified, the netlist.lib file will be saved to
        the specified file path.
        Returns the lib netlist.
        """
        with open(self.netlist_filepath) as netlist_file:
            netlist = netlist_file.read()
        netlist = self._update_top_level_subckt(netlist)
        if lib_filepath is not None:
            with open(lib_filepath,"w") as lib_file:
                lib_file.write(netlist)
        # TODO: We might want to remove any control and ".global" commands
        return netlist
        
    @staticmethod
    def _update_top_level_subckt(netlist: str) -> str:
        netlist.replace("**.subckt", ".subckt")
        netlist.replace("**.ends", ".ends")
        return netlist
    
    def export_svg(path: Union[Path, str], 
                   log_path: optional_path = None) -> None:
        #sch_picture_path = self.netlist_dirpath.parent / \
        #                   (self.schematic_path.stem + ".svg")
        options = ["-q","--svg","--plotfile",str(path)]
        if log_path is not None:
            options = options.extend(["-l", str(log_path)])
        run_result=subprocess.run(["xschem"].extend(options), 
                                  capture_output=True, check=True)

    @staticmethod
    def tool_is_available() -> bool:
        run_result=subprocess.run(["xschem", "--version"],
                       capture_output=True, check=False)
        return run_result.returncode == 0

    @staticmethod
    def tool_version() -> bool:
        run_result=subprocess.run(["xschem", "--version"],
                       capture_output=True, check=False)
        return run_result.returncode == 0

    @classmethod
    def check_tool_is_available(cls) -> None:
        if not cls.tool_is_available():
            raise Exception(
                """Xschem is not available!\n
                   Please make sure  the xschem binary is on $PATH""")

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def netlisting_log_path(self):
        return self.netlist_dirpath \
               / (self.name + ".netlisting.log")
    
    @property
    def netlist_filepath(self):
        return self.netlist_dirpath / (self.name + ".spice")


    def _parse_subckt(self, netlist: str, name: str) -> dict:
        pass
