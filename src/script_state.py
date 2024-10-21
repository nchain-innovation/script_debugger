""" This holds the interpreted script
"""
import logging
from typing import List, Union
from tx_engine import Script
from tx_engine.engine.op_code_names import OP_CODE_NAMES
from util import has_extension


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


class ScriptState():
    """ This holds the interpreted script, provides load and list methods.
    """
    def __init__(self):
        """ Setup the script state
        """
        self.script = None

    def load_file(self, filename: str) -> None:
        """ Load loaded file, but don't parse it
        """
        try:
            # load it
            with open(filename, "r", encoding="utf-8") as f:
                contents = f.readlines()
        except FileNotFoundError as e:
            print(e)
        else:
            if has_extension(filename, "bs"):
                self.parse_script(contents)

    def parse_script(self, contents: List[str]) -> None:
        """ Parse provided contents
        """
        if contents:
            # parse contents
            line: str = " ".join(contents)
            self.script = Script.parse_string(line)

    def list(self) -> None:
        """ Prints out script
        """
        if self.script:
            cmds = self.script.get_commands()
            indent = 0
            for i, cmd in enumerate(cmds):
                indent = print_cmd(i, cmd, indent)
        else:
            print("No file loaded.")

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
