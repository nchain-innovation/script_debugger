""" This holds the interpreted script
"""
import logging
from typing import List, Union, Any
import bitcoin_script_parser.bitcoin_script_parser
from tx_engine import Script
from tx_engine.engine.op_code_names import OP_CODE_NAMES
from util import has_extension
import bitcoin_script_parser

LOGGER = logging.getLogger(__name__)


def cmd_repr(cmd: int) -> Union[str, bytes]:
    """ Return a string (and bytes) representation of the command
        e.g. 0x5 -> OP_10
    """
    if isinstance(cmd, int):
        try:
            return OP_CODE_NAMES[cmd]
        except KeyError:
            return str(cmd)
    else:
        return cmd


def print_cmd(i: int, cmd, indent: int = 0) -> int:
    """ Prints the command and manages the indent
    """
    cmd = cmd_repr(cmd)
    if isinstance(cmd, str):
        if cmd in ("OP_ELSE", "OP_ENDIF"):
            indent -= 2
        print(f"{i}: {' ' * indent}{cmd}")
        if cmd in ("OP_IF", "OP_NOTIF", "OP_ELSE"):
            indent += 2
    else:
        print(f"{i}: {' ' * indent}{int.from_bytes(cmd, byteorder='little')} (0x{cmd.hex()}, {cmd})")
    return indent

def format_cmds(script_str: str) -> str:
    lines = script_str.split() # split by whitespaces
    formatted_script: List = []
    indent: int = 0
    for op in lines:
        if op in ["OP_IF", "OP_NOTIF"]:
            formatted_script.append(' ' * indent + op)
            indent += 2
        elif op == "OP_ELSE":
            # decrease before printing, OP_ELSE, increase afterwards
            indent -= 2
            formatted_script.append(' ' * indent + op)
            indent += 2
        elif op == "OP_ENDIF":
            # decreate indentation befre printing
            indent -= 2
            formatted_script.append(' ' * indent + op)
        else:
            # just print
            formatted_script.append(' ' * indent + op)
    return '\n'.join(formatted_script)

class ScriptState():
    """ This holds the interpreted script, provides load and list methods.
        This class has been extended to include the full script & the script after each debug stage 
    """
    def __init__(self):
        """ Setup the script state
        """
        self.script = None # this is loaded from the file & remains unchanged
        # instruction location
        self.instruction_offset: List[Any] = []

    def load_file(self, filename: str) -> None:
        """ Load loaded file, but don't parse it
        """
        try:
            # load it
            with open(filename, "r", encoding="utf-8") as f:
                # contents = f.readlines()
                contents = [line.strip() for line in f.readlines()]
        except FileNotFoundError as e:
            print(e)
        else:
            if has_extension(filename, "bs"):
                # self.parse_script(contents)
                self.parse_script_new(contents)

    def parse_script_new(self, contents: List[str]) -> None:
        """ Parse provided contents
        """
        if contents:
        # Initialize an empty script or container to hold the full script
            self.script = Script() 
            # Iterate through each line and process it, adding each part to the script
            for line in contents:
                #print(f'{line}')
                tmp_script = Script.parse_string(line)
                self.script += tmp_script

        # set up the instruction offsets
        script_str = self.script.to_string()
        print(f'parse_script_new -> {script_str}')
        self.instruction_offset =  bitcoin_script_parser.bitcoin_script_parser.parse_script(self.script.to_string())

    def list_full(self) -> None:
        if self.script:
            script_str: str = self.script.to_string()
            print(format_cmds(script_str))

    def get_commands(self):
        """ Return commands associated with this script
        """
        if self.script:
            return self.script.get_commands()
        return []

    def set_commands(self, cmds):
        """ Set the commands associated with this script
        """
        if self.script is None:
            self.script = Script()
        self.script.cmds = cmds

#OP_PUSHDATA4 0x04000000 0xaabbccdd
