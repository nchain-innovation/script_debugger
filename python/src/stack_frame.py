""" This contains the stack frame from which the script operates
"""
from typing import Optional, List, Tuple
from tx_engine import Context
from tx_engine.engine.engine_types import Command
from breakpoints import Breakpoints


class StackFrame:
    """ This is the state of a script
    """
    def __init__(self, name: str = "main"):
        """ Setup StackFrame
        """
        self.name: str = name
        self.context = Context()
        self.breakpoints: Breakpoints = Breakpoints()

        # instruction_count -> the number of instructions executed so far,
        # which is also the index of the next operation in instruction_offset.
        # None means the script has not been prepared to run.
        self.instruction_count: Optional[int] = None
        # (opcode mnemonic, byte offset into the serialised script)
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
        """ Return True if the script has not finished.
            The instruction_count is compared with the number of entries in
            instruction_offset.
        """
        if self.instruction_count is None:
            return False
        return self.instruction_count < len(self.instruction_offset)

    def get_cmd(self) -> Command:
        """ Return the current command
        """
        assert isinstance(self.instruction_count, int)
        return self.context.cmds[self.instruction_count]

    def current_opcode(self) -> Optional[str]:
        """ Return the mnemonic of the operation about to execute, or None if
            execution has run off the end of the script.
        """
        if self.instruction_count is None:
            return None
        if not 0 <= self.instruction_count < len(self.instruction_offset):
            return None
        return self.instruction_offset[self.instruction_count][0]

    def print_cmd(self) -> None:
        """ Print the current command
        """
        opcode = self.current_opcode()
        if opcode is None:
            print("OP Code -> <end of script>")
        else:
            print(f"OP Code -> {opcode}")

    def print_breakpoint(self) -> None:
        """ Print the breakpoint that has just been hit
        """
        opcode = self.current_opcode()
        print(f"Instruction Pointer -> {self.instruction_count} - "
              f"Hit breakpoint {self.breakpoints.current_bp_index}: {opcode}")

    def hit_breakpoint(self) -> bool:
        """ Return True if execution has stopped on a breakpoint
        """
        if self.instruction_count is None:
            return False
        return self.breakpoints.hit(self.instruction_count)
