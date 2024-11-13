""" This contains the stack frame from which the script operates
"""
from typing import Optional, List, Tuple, Union
from tx_engine import Context
from tx_engine.engine.engine_types import Command
from breakpoints import Breakpoints
from tx_engine.engine.op_code_names import OP_CODE_NAMES

#from script_state import ScriptState, print_cmd
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


class StackFrame:
    """ This is the state of a script
    """
    def __init__(self, name: str = "main"):
        """ Setup StackFrame
        """
        self.name: str = name
        # self.script_state: ScriptState = ScriptState()
        self.context = Context()
        self.breakpoints: Breakpoints = Breakpoints()

        # instruction_count -> means the number of instructions executed
        self.instruction_count: Optional[int] = None
        # instruction_index into the script (in bytes), breakpoints can only be set on these locations. 
        # for ease of use, the breakpoint will be the instruction number (displayed on screen?)
        # this value is then used to index into this array
        self.instruction_offset: List[Tuple[str, int]] = []

    def __repr__(self) -> str:
        if self.name == "main":
            return "(main)"
        return f"(FNCALL='{self.name}')"

    def reset_core(self) -> None:
        """ Reset the script ready to run
        """
        #self.context.set_commands(self.script_state.script)
        self.instruction_count = 0
       

        # set the script for the next 
        # self.context.set_commands(self.script_state.script_after_debug_step)

    def reset_stacks(self) -> None:
        """ Reset the associated stacks
        """
        self.context.reset_stacks()

    def can_run(self) -> bool:
        """ Return true if script has not finished
            To determine finised, the instruction_count is compared with the 
            number of entries in ScriptState.instruction_offset
        """ 
        assert isinstance(self.instruction_count, int)
        return self.instruction_count < len(self.instruction_offset)

    def get_cmd(self) -> Command:
        """ Return the current command
        """
        assert isinstance(self.instruction_count, int)
        return self.context.cmds[self.ip]

    def print_cmd(self) -> None:
        """ Print the current command
        """
        assert isinstance(self.ip, int)
        print_cmd(self.ip, self.context.cmds[self.ip])

    def print_breakpoint(self) -> None:
        """ Print the hit breakpoint
        """
        assert isinstance(self.ip, int)
        print(f"{self.ip} - Hit breakpoint: {self.breakpoints.get_associated(self.ip)}", end=" ")
        self.print_cmd()

    def hit_breakpoint(self) -> bool:
        """ Return true if hit breakpoint
        """
        assert isinstance(self.ip, int)
        return self.breakpoints.hit(self.ip)
