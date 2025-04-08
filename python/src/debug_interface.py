""" This provides an interface to the debugger
"""
from enum import Enum
import logging
import sys
try:
    import readline  # noqa: F401
    # Note readline is not used but including it enables 'input()' command history.
except ModuleNotFoundError:
    pass

from typing import List

from debug_context import DebuggingContext
from util import has_extension


LOGGER = logging.getLogger(__name__)

USAGE = """ usage: ./debugger.py -file <input_file.ms>"

This program allows the user to debug a bitcoin script file.
"""


HELP = """
This is the bitcoin script debugger help

h, help -- Prints this message.
q, quit, exit -- Quits the program.

file <filename> -- Loads the specified script file for debugging.
list -- List the current script file contents.
listops -- List the op codes and their positions to set breakpoints.
run -- Runs the current loaded script until breakpoint or error.

hex -- Display the main stack in hexidecimal values.
bytes -- Display the main stack in bytes.
dec -- Display the main stack in decimal values.

sstart <n> -- Set the start index for stack display (counting from top of the stack); -1 for bottom of the stack.
send <n> -- Set the end index for stack display (counting from top of the stack).

reset -- Reset the script to the staring position.
s -- Step over the next instruction.
c -- Continue the current loaded script until breakpoint or error.
b <n>-- Adds a breakpoint on the nth operation.
info break -- List all the current breakpoints.
d <n> -- Deletes breakpoint number n.
loc -- Gives the current OP_CODE and location
"""

class DebuggerFormat(Enum):
    """ Enum for the format of the debugger
    """
    BYTES = 0
    HEX = 1
    DECIMAL = 2

class DebuggerInterface:
    """ Provides the interface to the debugger
    """
    def __init__(self):
        """ Initial setup
        """
        self.db_context = DebuggingContext()
        # Debugger format
        self.format = DebuggerFormat.DECIMAL
        # Stack indices
        self.stack_start = None
        self.stack_end = 1

    def set_noisy(self, boolean: bool) -> None:
        """ Set the noisy flag, set to false in unit tests to prevent printouts
        """
        self.db_context.noisy = boolean

    def print_status(self) -> None:
        """ Print out the current stack contents
        """
        stack_start = self.stack_start if self.stack_start is not None else self.db_context.get_stack().size()
        match (self.stack_start, self.stack_end):
            case (None, 1):
                slice_str = ""
            case (None, _):
                slice_str = f"[:-{self.stack_end}]"
            case (_, 1):
                slice_str = f"[-{stack_start}:]"
            case (_, _):
                slice_str = f"[-{stack_start} : -{self.stack_end}]"
        match self.format:
            case DebuggerFormat.BYTES:
                print(f"stack(bytes){slice_str} = {[self.db_context.get_stack()[i] for i in range(self.db_context.get_stack().size() - stack_start, self.db_context.get_stack().size() - self.stack_end + 1)]}, altstack = {self.db_context.get_altstack()}")
            case DebuggerFormat.HEX:
                # Print stack in hex form
                print(f"stack(hex){slice_str} = {[['0x' + ''.join(f'{n:02x}' for n in self.db_context.get_stack()[i])] for i in range(self.db_context.get_stack().size() - stack_start, self.db_context.get_stack().size() - self.stack_end + 1)]}")
                print(f"altstack = {[['0x' + ''.join(f'{n:02x}' for n in inner_list)] for inner_list in self.db_context.get_altstack()]}")
            case DebuggerFormat.DECIMAL:
                # Print stack in decimal form
                print(f"stack(dec){slice_str} = {[int.from_bytes(self.db_context.get_stack()[i], "little") for i in range(self.db_context.get_stack().size() - stack_start, self.db_context.get_stack().size() - self.stack_end + 1)]}")
                print(f"altstack = {[int.from_bytes(inner_list, "little") for inner_list in self.db_context.get_altstack()]}")

    def load_script_file(self, fname: str) -> None:
        """ Load a script file
        """
        bits = fname.split(".")

        if len(bits) > 1:
            if bits[-1] not in ("bs"):
                print(f"Wrong file extension: {fname}")
            else:
                if self.db_context.noisy:
                    print(f"Loading filename: {fname}")
                self.db_context.load_script_file(fname)
        else:
            print(f"No file extension: {fname}")

    def has_script(self) -> bool:
        """ Return True if we have a script loaded.
        """
        return self.db_context.has_script()

    def run(self) -> None:
        """ Run a script
        """
        if self.has_script():
            self.db_context.reset()
            self.db_context.run()
        else:
            print("No script loaded.")

    def reset(self) -> None:
        """ Reset debugger to start of script
        """
        LOGGER.info("reset")
        if self.has_script():
            self.db_context.reset()
        else:
            print("No script loaded.")

    def step(self) -> None:
        """ Step over the next operation.
        """
        if not self.has_script():
            print("No script loaded.")
            return

        if self.db_context.is_not_runable():
            print('db_interface.step Reseting script')
            self.db_context.reset()

        if self.db_context.can_run():
            self.db_context.step()
        else:
            print('At end of script, use "reset" to run again.')

    def continue_script(self) -> None:
        """ Continue - but we can't use that word
        """
        if not self.has_script():
            print("No script loaded.")
            return

        if self.db_context.is_not_runable():
            self.db_context.reset()

        if self.db_context.can_run():
            # step to step over current breakpoint
            self.db_context.continue_script()
        else:
            print('At end of script, use "reset" to run again.')

    def add_breakpoint(self, user_input: List[str]) -> None:
        """ Add a breakpoint
        """
        if not self.has_script():
            print("No script loaded.")
            return

        if len(user_input) < 2:
            print("Breakpoint location not set")
            return

        n = int(user_input[1])
        if n >= self.db_context.get_number_of_operations():
            print('Breakpoint beyond end of script.')
            return

        bpid = self.db_context.breakpoints.add(n)
        if bpid is None:
            print("Breakpoint already present at this address.")
        else:
            if self.db_context.noisy:
                print(f"Added breakpoint {bpid} at {n}")

    def list_breakpoints(self) -> None:
        """ List all breakpoints
        """
        bps = self.db_context.breakpoints.get_all()
        if len(bps) == 0:
            print("No breakpoints.")
        else:
            for op_number, b in enumerate(bps, start=0):
                print(f"Breakpoint: {op_number} operation number: {b} op code: { self.db_context.sf.instruction_offset[b][0]}")

    def delete_breakpoint(self, user_input: List[str]) -> None:
        """ Delete a breakpoint
        """
        if len(user_input) < 2:
            print("Provide the n of the breakpoint to delete.")
        else:
            try:
                n = int(user_input[1].strip())
                # delete the breakpoint at the given index.
                if n > len(self.db_context.breakpoints.breakpoints):
                    print(f'No breakpoint at {n}')
                    return
                del self.db_context.breakpoints.breakpoints[n]
            except ValueError:
                print("Invalid string to number conversion")

    def execution_location(self) -> None:
        assert (self.db_context.sf.instruction_count is not None)
        print(f'Instruction Number -> {self.db_context.sf.instruction_count}')
        if self.db_context.sf.instruction_count >= len(self.db_context.sf.instruction_offset):
            print('Instruction count beyond the end of the script')
        else:
            print(f'Instruction Number -> {self.db_context.sf.instruction_count}')
            print(f'Op Code -> {self.db_context.sf.instruction_offset[self.db_context.sf.instruction_count][0]}')

    def process_input(self, user_input: List[str]) -> None:
        """ process user input
        """
        if user_input[0] in ("h", "help"):
            print(HELP)
        elif user_input[0] == "file":
            if len(user_input) < 2:
                print("The file command requires a filename.")
            else:
                self.load_script_file(user_input[1])
        elif user_input[0] == "list":
            self.db_context.list()
        elif user_input[0] == "listops":
            self.db_context.list_ops()
        elif user_input[0] == "info" and user_input[1] == "break":
            self.list_breakpoints()
        elif user_input[0] == "bytes":
            self.format = DebuggerFormat.BYTES
        elif user_input[0] == "hex":
            self.format = DebuggerFormat.HEX
        elif user_input[0] == "dec":
            self.format = DebuggerFormat.DECIMAL
        elif user_input[0] == "reset":
            self.reset()
        elif user_input[0] in ("r", "run"):
            self.run()
        elif user_input[0] in ("s", "step"):
            self.step()
        elif user_input[0] == "c":
            self.continue_script()
        elif user_input[0] == "b":
            self.add_breakpoint(user_input)
        elif user_input[0] == "d":
            self.delete_breakpoint(user_input)
        elif user_input[0] == "loc":
            self.execution_location()
        elif user_input[0] == "sstart":
            self.stack_start = None if int(user_input[1]) == -1 else int(user_input[1])
        elif user_input[0] == "send":
            self.stack_end = int(user_input[1])
        else:
            print(f'Unknown command "{user_input[0]}"".')

    def read_eval_print_loop(self) -> None:
        """ Main print-read-eval loop of debugger.
        """
        while True:
            self.print_status()
            user_input = input("(gdb) ")
            split_input: List[str] = user_input.strip().split()
            if len(split_input) == 0:
                pass
            elif split_input[0] in ("q", "quit", "exit"):
                break
            else:
                self.process_input(split_input)

    def load_files_from_list(self, filenames: List[str]) -> None:
        """ Parse the provided list of filenames and load script files.
        """
        # print(f"filenames={filenames}")
        for fname in filenames:
            # determine the file extension
            if has_extension(fname, "bs") or has_extension(fname, "ms"):
                self.load_script_file(fname)
            else:
                print(f"Unknown file type: {fname}")
                print(USAGE)
                sys.exit()
