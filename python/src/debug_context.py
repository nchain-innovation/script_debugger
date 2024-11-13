""" Contains the state of the current debugging session
"""

import logging
from typing import Optional

from tx_engine import Script
from stack_frame import StackFrame
from breakpoints import Breakpoints

LOGGER = logging.getLogger(__name__)


class DebuggingContext:
    """ This is the state of the current debugging session
    """
    def __init__(self):
        """ Intial setup
        """
        self.noisy: bool = True  # print operations as they are executed
        self.sf = StackFrame()

    def get_stack(self):
        """ Return the main stack
        """
        return self.sf.context.get_stack()


    def get_altstack(self):
        """ Return the alt stack
        """
        return self.sf.context.get_altstack()

    @property
    def breakpoints(self) -> Breakpoints:
        """ Provides access to the breakpoints in the current stack frame
        """
        return self.sf.breakpoints

    @property
    def ip(self) -> Optional[int]:
        """ Returns the current Instruction Pointer
        """
        return self.sf.script_state.instruction_offset[self.sf.instruction_count]
    
    @property
    def instruction_count(self) -> Optional[int]:
        """ Returns the current Instruction count
        """
        return self.sf.instruction_count

    def step(self) -> bool:
        """ Step over the next instruction
            Return True if operation was successful
        """
        if self.noisy:
            self.sf.print_cmd()

        # Next instruction
        assert isinstance(self.sf.instruction_count, int)
        self.sf.context.ip_start = self.sf.script_state.instruction_offset[self.sf.instruction_count][1]
        self.sf.instruction_count += 1
        # ip_limit -> This is how far (in bytes to step)
        print(f'debug_context.step -> instruction count -> {self.sf.instruction_count}')
        print(f'debug_context.step -> instruction offset -> {self.sf.script_state.instruction_offset}')

        # to handle the last element
        if self.sf.instruction_count == len(self.sf.script_state.instruction_offset):
            self.sf.context.ip_limit = None
        else:
            self.sf.context.ip_limit = self.sf.script_state.instruction_offset[self.sf.instruction_count][1]
        exec_step: bool = self.sf.context.evaluate_core()
        print(f'Value in db_context.step of sf.context.ip_limit {self.sf.context.ip_limit}')
        return exec_step

    def reset(self) -> None:
        """ Reset the script ready to run - interface to Debugger
        """
        LOGGER.info("debug_context - reset")
        self.sf.reset_core()
        self.sf.reset_stacks()

    def can_run(self) -> bool:
        """ Return true if script has not finished
        """
        return self.sf.can_run()

    def get_next_breakpoint(self) -> None | int:
        """ Based on the current ip determine the next breakpoint
        """

    def run(self) -> None:
        """ Run the script
        """
        # Check for breakpoints
        if self.sf.instruction_count is None:
            self.sf.instruction_count = 0

        next_bp = self.sf.breakpoints.get_next_breakpoint(self.sf.instruction_count)
        if next_bp is None:
            self.sf.context.ip_limit = None
            self.sf.instruction_count = 0
        else:
            self.sf.context.ip_limit = next_bp
            self.sf.instruction_count = next_bp
        succ = self.sf.context.evaluate_core()
        if not succ:
            print("Operation failed.")
        else:
            if self.sf.hit_breakpoint() and self.noisy:
                self.sf.print_breakpoint()

    def get_number_of_operations(self) -> int:
        """ Return the number of operatations in this script
        """
        return len(self.sf.script_state.get_commands())

    def interpret_line(self, user_input: str) -> None:
        """ Interpret the provided line in separate context.
        """
        try:
            script = Script.parse_string(user_input)
        except NameError as e:
            print(e)
            return

        self.sf.context.set_commands(script)
        if not self.sf.context.evaluate_core():
            print("Operation failed")

    def has_script(self) -> bool:
        """ Return True if we have a script loaded.
        """
        return self.sf.script_state.script is not None

    def is_not_runable(self) -> bool:
        """ Return True if script is not runable
        """
        return self.sf.instruction_count is None

    def list(self) -> None:
        """ List the commands
        """
        self.sf.script_state.list_full()

    def load_script_file(self, fname) -> None:
        """ Load script file from fname
            Reset the breakpoints as these will no longer be relevant
            Load any use(d) library files
        """
        self.sf.script_state.load_file(fname)
        self.reset()
        self.sf.breakpoints.reset_all()