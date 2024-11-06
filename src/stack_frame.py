""" This contains the stack frame from which the script operates
"""
from typing import Optional
from tx_engine import Context
from tx_engine.engine.engine_types import Command
from breakpoints import Breakpoints

from script_state import ScriptState, print_cmd


class StackFrame:
    """ This is the state of a script
    """
    def __init__(self, name: str = "main"):
        """ Setup StackFrame
        """
        self.name: str = name
        self.script_state: ScriptState = ScriptState()
        self.context = Context()
        self.breakpoints: Breakpoints = Breakpoints()

        # instruction_count -> means the number of instructions executed
        self.instruction_count: Optional[int] = None
        

    def __repr__(self) -> str:
        if self.name == "main":
            return "(main)"
        return f"(FNCALL='{self.name}')"

    def reset_core(self) -> None:
        """ Reset the script ready to run - ignore the stack frame - script_state.const_script doesn't change
        """
        self.context.set_commands(self.script_state.script)
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
        assert isinstance(self.ip, int)
        return self.instruction_count < len(self.script_state.instruction_offset)

    def get_cmd(self) -> Command:
        """ Return the current command
        """
        assert isinstance(self.ip, int)
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
