""" Contains the state of the current debugging session
"""

import logging
from typing import Optional

from tx_engine import Script
from stack_frame import StackFrame
from breakpoints import Breakpoints
from util import load_file, list_full
from bitcoin_script_parser import parse_script

LOGGER = logging.getLogger(__name__)


class DebuggingContext:
    """ This is the state of the current debugging session
    """
    def __init__(self):
        """ Initial setup
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
        """ Return the byte offset of the next operation to execute, or the
            number of operations once the script has run to the end.
        """
        if self.sf.instruction_count is None:
            return None
        if self.sf.instruction_count >= len(self.sf.instruction_offset):
            return len(self.sf.instruction_offset)
        return self.sf.instruction_offset[self.sf.instruction_count][1]

    @property
    def instruction_count(self) -> Optional[int]:
        """ Return the current instruction count
        """
        return self.sf.instruction_count

    def _byte_offset_of(self, op_number: int) -> Optional[int]:
        """ Return the byte offset of operation `op_number`, or None for the
            end of the script (which tx_engine spells as an ip_limit of None).
        """
        if op_number >= len(self.sf.instruction_offset):
            return None
        return self.sf.instruction_offset[op_number][1]

    def step(self) -> bool:
        """ Step over the next instruction.
            Return True if the operation was successful.
        """
        if not self.can_run():
            return False

        if self.noisy:
            self.sf.print_cmd()

        assert isinstance(self.sf.instruction_count, int)
        start = self.sf.instruction_offset[self.sf.instruction_count][1]
        # If the first reported operation is not at byte 0 the script opens
        # with data pushes, which have to execute before it.
        if self.sf.instruction_count == 0:
            start = 0
        self.sf.context.ip_start = start

        self.sf.instruction_count += 1
        self.sf.context.ip_limit = self._byte_offset_of(self.sf.instruction_count)
        return self.sf.context.evaluate_core()

    def reset(self) -> None:
        """ Reset the script ready to run - interface to Debugger
        """
        LOGGER.info("debug_context - reset")
        self.sf.reset_core()
        self.sf.reset_stacks()
        self.sf.breakpoints.current_bp_index = 0

    def can_run(self) -> bool:
        """ Return True if the script has not finished
        """
        return self.sf.can_run()

    def _start_offset(self) -> int:
        """ Byte offset execution should resume from.

            Operation 0 always starts at byte 0: if the script opens with data
            pushes the first *operation* sits further in, and starting there
            would skip the pushes it consumes.
        """
        assert isinstance(self.sf.instruction_count, int)
        if self.sf.instruction_count == 0:
            return 0
        return self._byte_offset_of(self.sf.instruction_count) or 0

    def _run_to(self, next_bp: Optional[int]) -> None:
        """ Execute from the current position up to `next_bp`, or to the end
            of the script if `next_bp` is None.
        """
        assert isinstance(self.sf.instruction_count, int)
        if not self.can_run():
            print('At end of script, use "reset" to run again.')
            return

        self.sf.context.ip_start = self._start_offset()
        self.sf.context.ip_limit = (
            None if next_bp is None else self._byte_offset_of(next_bp)
        )

        if not self.sf.context.evaluate_core():
            print("Operation failed.")
            return

        # Park the instruction pointer where execution actually stopped, so a
        # subsequent step or continue picks up from the right place. Leaving it
        # at 0 after a completed run made can_run() lie and re-executed the
        # script from the top on the next step.
        self.sf.instruction_count = (
            len(self.sf.instruction_offset) if next_bp is None else next_bp
        )

        if next_bp is not None and self.noisy and self.sf.hit_breakpoint():
            self.sf.print_breakpoint()

    def continue_script(self) -> None:
        """ Continue execution to the next breakpoint, or to the end.
        """
        if self.sf.instruction_count is None:
            self.run()
            return
        # inclusive=False: we are sitting on a breakpoint and must move past it.
        self._run_to(self.sf.breakpoints.get_next_breakpoint(
            self.sf.instruction_count, inclusive=False))

    def run(self) -> None:
        """ Run the script from the current position
        """
        if self.sf.instruction_count is None:
            self.sf.instruction_count = 0
        # inclusive=True: a breakpoint on the current operation must be honoured.
        self._run_to(self.sf.breakpoints.get_next_breakpoint(
            self.sf.instruction_count, inclusive=True))

    def get_number_of_operations(self) -> int:
        """ Return the number of operations in this script.
            Data pushes are not counted.
        """
        return len(self.sf.instruction_offset)

    def has_script(self) -> bool:
        """ Return True if we have a script loaded.
        """
        if self.sf.context.cmds is None:
            return False
        return len(self.sf.context.cmds) > 0

    def is_not_runable(self) -> bool:
        """ Return True if the script is not runnable
        """
        return self.sf.instruction_count is None

    def list(self) -> None:
        """ List the commands
        """
        if not self.has_script():
            print("No script loaded.")
            return
        list_full(Script(self.sf.context.cmds))

    def list_ops(self) -> None:
        """ List the operations and their numbers, for setting breakpoints.
        """
        if not self.sf.instruction_offset:
            print("No script loaded.")
            return
        print(f"{'Op Code Number':>16}  {'Byte Offset':>11}  Op Code")
        for op_number, (opcode, offset) in enumerate(self.sf.instruction_offset):
            print(f"{op_number:>16}  {offset:>11}  {opcode}")

    def load_script_file(self, fname: str) -> bool:
        """ Load the script file `fname`, resetting the breakpoints since they
            will no longer be relevant. Returns True on success.
        """
        script_to_dbg = load_file(fname)
        if script_to_dbg is None:
            return False

        debug_str = script_to_dbg.to_debug_parser_string()
        try:
            instruction_offset = parse_script(debug_str)
        except ValueError as e:
            print(f"Failed to parse '{fname}': {e}")
            return False

        self.sf.context.set_commands(script_to_dbg)
        self.sf.instruction_offset = instruction_offset
        self.reset()
        self.sf.breakpoints.reset_all()
        if self.noisy:
            print(f"Loaded {fname}: {self.get_number_of_operations()} operations, "
                  f"{len(self.sf.context.cmds)} bytes.")
        return True
