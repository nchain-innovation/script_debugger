""" This contains the stack frame from which the script operates
"""
from typing import Optional, List, Tuple, Union
from tx_engine import Context
from tx_engine.engine.engine_types import Command
from breakpoints import Breakpoints
from tx_engine.engine.op_code_names import OP_CODE_NAMES


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
        self.instruction_offset: List[Tuple[str, int]] = []

    def __repr__(self) -> str:
        if self.name == "main":
            return "(main)"
        return f"(FNCALL='{self.name}')"

    def reset_core(self) -> None:
        """ Reset the script ready to run
        """
        self.instruction_count = 0
        self.context.ip_start = 0
        self.context.ip_limit = None

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
        return self.context.cmds[self.instruction_count]

    def print_cmd(self) -> None:
        """ Print the current command
        """
        assert isinstance(self.instruction_count, int)
        print(f"OP Code -> {self.instruction_offset[self.instruction_count][0]}")

    def print_breakpoint(self) -> None:
        """ Print the hit breakpoint
        """
        assert isinstance(self.instruction_count, int)
        print(f'{self.breakpoints.get_all()}')
        print(f'BP Index -> {self.breakpoints.current_bp_index}')
        assert (self.instruction_count == self.breakpoints.breakpoints[self.breakpoints.current_bp_index])
        print(f"Instruction Pointer -> {self.instruction_count} - Hit breakpoint: {self.instruction_offset[self.instruction_count][0]}", end=" ")
        self.print_cmd()

    def hit_breakpoint(self) -> bool:
        """ Return true if hit breakpoint
        """
        assert isinstance(self.instruction_count, int)
        return self.breakpoints.hit(self.instruction_count)
