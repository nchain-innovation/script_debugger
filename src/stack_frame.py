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
        self.ip: Optional[int] = None

    def __repr__(self) -> str:
        if self.name == "main":
            return "(main)"
        return f"(FNCALL='{self.name}')"

    def reset_core(self) -> None:
        """ Reset the script ready to run - ignore the stack frame
        """
        self.context.set_commands(self.script_state.get_commands())
        self.ip = 0

    def reset_stacks(self) -> None:
        """ Reset the associated stacks
        """
        self.context.reset_stacks()

    def can_run(self) -> bool:
        """ Return true if script has not finished
        """
        assert isinstance(self.ip, int)
        return self.ip < len(self.context.cmds)

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
