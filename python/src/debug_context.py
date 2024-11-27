""" Contains the state of the current debugging session
"""

import logging
from typing import Optional

from tx_engine import Script
from stack_frame import StackFrame
from breakpoints import Breakpoints
from util import load_file, list_full
import bitcoin_script_parser

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
        """ Returns the current Instruction Pointer (the second element in the tuple)
        """
        assert (self.sf.instruction_count is not None)
        if self.sf.instruction_count >= len(self.sf.instruction_offset):
            return len(self.sf.instruction_offset)
        return self.sf.instruction_offset[self.sf.instruction_count][1]
    
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

        # the instruction count start & end must always be based on the instruction offset
        # if the there is raw data at the beginning of the script in particular. 
        assert isinstance(self.sf.instruction_count, int)
        if self.sf.instruction_count == 0:
            # if the first opcode is not element zero the start point has to be the beginning of the script
            if self.sf.instruction_offset[self.sf.instruction_count][1] != 0:
                self.sf.context.ip_start = 0
            else:
                self.sf.context.ip_start = self.sf.instruction_offset[self.sf.instruction_count][1]
        else:
            self.sf.context.ip_start = self.sf.instruction_offset[self.sf.instruction_count][1]
            
        self.sf.instruction_count += 1

        # to handle the last element
        if self.sf.instruction_count == len(self.sf.instruction_offset):
            self.sf.context.ip_limit = None
        else:
            self.sf.context.ip_limit = self.sf.instruction_offset[self.sf.instruction_count][1]
        exec_step: bool = self.sf.context.evaluate_core()
        # print(f'Value in db_context.step of sf.context.ip_limit {self.sf.context.ip_limit}')
        return exec_step

    def reset(self) -> None:
        """ Reset the script ready to run - interface to Debugger
        """
        LOGGER.info("debug_context - reset")
        self.sf.reset_core()
        self.sf.reset_stacks()
        self.sf.breakpoints.current_bp_index = 0

    def can_run(self) -> bool:
        """ Return true if script has not finished
        """
        return self.sf.can_run()

    #def get_next_breakpoint(self) -> None | int:
    #    """ Based on the current ip determine the next breakpoint
    #    """

#if next_breakpoint is None:
        # No further breakpoints, return current counter
#        return instruction_counter

    # Calculate number of instructions between current_offset and next_breakpoint
#    instructions_to_next = sum(
#        1 for _, offset in opcodes_offsets 
#        if current_offset < offset <= next_breakpoint
#    )
    
    # Increment instruction counter
#    return instruction_counter + instructions_to_next


    def continue_script(self) -> None:
        # if the script is not yet executed .. run from the beginning
        if self.sf.instruction_count is None:
            self.run()
        else:
            # Start at current location upto the next breakpoint or
            next_bp = self.sf.breakpoints.get_next_breakpoint(self.sf.instruction_count)
            if next_bp is None:
                # no more break points. run ffrom the current location to the end.
                print('No more break points')
                print(f'Setting ip_start to instruction_count {self.sf.instruction_count}')
                self.sf.context.ip_limit = None
                self.sf.context.ip_start = self.sf.instruction_offset[self.sf.instruction_count][1]
            else:
                print('Setting te next  start & end for the script')
                
                self.sf.context.ip_limit = self.sf.instruction_offset[next_bp][1]
                self.sf.context.ip_start = self.sf.instruction_offset[self.sf.instruction_count][1]
                print(f'Stating at {self.sf.context.ip_start}\nEnding at {self.sf.context.ip_limit }')

            succ = self.sf.context.evaluate_core()
            if not succ:
                print("Operation failed.")
            # set the ip pointer?
            # hit a breakpoint and I want to see the instruction-counter
            # which is the index of the op_code in instruction_offset and the index is given by the breakpoint
            if next_bp is None:
                # no more breakpoints .. set to the one past the lenght of the instruction_offset?
                self.sf.instruction_count = len(self.sf.instruction_offset)
            else:
                # this line is not correct .. it sets the instruction count to the script location
                # self.sf.instruction_count += abs(self.sf.instruction_offset[next_bp][1] - self.sf.instruction_count)
                self.sf.instruction_count = self.sf.breakpoints.breakpoints[self.sf.breakpoints.current_bp_index]

    def run(self) -> None:
        """ Run the script
        """
        # not yet executed
        if self.sf.instruction_count is None:
            self.sf.instruction_count = 0

        if self.sf.instruction_count == 0:
            # self.sf.context.ip_start = self.sf.instruction_offset[0][1]
            self.sf.context.ip_start = None
        # Check for breakpoints
        next_bp = self.sf.breakpoints.get_next_breakpoint(self.sf.instruction_count)
        if next_bp is None:
            # no breakpoints set .. run to the end.
            self.sf.context.ip_limit = None
            self.sf.instruction_count = 0
        else:
            self.sf.context.ip_limit = self.sf.instruction_offset[next_bp][1]
            self.sf.instruction_count = next_bp
    
        # execute
        succ = self.sf.context.evaluate_core()

        if not succ:
            print("Operation failed.")
        else:
            # test for any breakpoints
            if len(self.sf.breakpoints.breakpoints) > 0:
                if self.sf.hit_breakpoint() and self.noisy:
                    self.sf.print_breakpoint()

    def get_number_of_operations(self) -> int:
        """ Return the number of operatations in this script
            Not the data elements
        """
        return len(self.sf.instruction_offset)

    def has_script(self) -> bool:
        """ Return True if we have a script loaded.
        """
        if self.sf.context.cmds is not None:
            return len(self.sf.context.cmds) > 0
        else:
            return False

    def is_not_runable(self) -> bool:
        """ Return True if script is not runable
        """
        return self.sf.instruction_count is None

    def list(self) -> None:
        """ List the commands
        """
        script: Script = Script(self.sf.context.cmds)
        list_full(script)

    def list_ops(self) -> None:
        print('\t\tOp Code Number\t\tOp Code')
        for line_number, (opcode, location) in enumerate(self.sf.instruction_offset, start=0):
            print(f"\t\t\t{line_number} \t\t{opcode}")

    def load_script_file(self, fname) -> None:
        """ Load script file from fname
            Reset the breakpoints as these will no longer be relevant
            Load any use(d) librarys files
        """
        script_to_dbg: Script = load_file(fname)
        print(f'load_script_file {script_to_dbg}')
        self.sf.context.set_commands(script_to_dbg)
        self.reset()
        self.sf.breakpoints.reset_all()
        # set up the instruction_offset
        self.sf.instruction_offset = bitcoin_script_parser.bitcoin_script_parser.parse_script(script_to_dbg.to_debug_parser_string())
