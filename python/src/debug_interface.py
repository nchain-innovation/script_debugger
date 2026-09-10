""" This provides an interface to the debugger
"""
import logging
import sys
try:
    import readline  # noqa: F401
    # Note readline is not used but importing it enables 'input()' history.
except ModuleNotFoundError:
    pass

from typing import List

from debug_context import DebuggingContext
from util import has_extension


LOGGER = logging.getLogger(__name__)

SCRIPT_EXTENSION = "bs"

USAGE = f""" usage: dbg.py -file <input_file.{SCRIPT_EXTENSION}>

This program allows the user to debug a bitcoin script file.
"""


HELP = """
This is the bitcoin script debugger help

h, help -- Print this message.
q, quit, exit -- Quit the program.

file <filename> -- Load the specified script file for debugging.
list -- List the current script file contents.
listops -- List the op codes and their positions, for setting breakpoints.
r, run -- Run the loaded script from the current position until a breakpoint
          or an error.

hex -- Display the main stack in hexadecimal.
dec -- Display the main stack in decimal.

reset -- Reset the script to the starting position.
s, step -- Step over the next instruction.
c -- Continue the loaded script until a breakpoint or an error.
b <n> -- Add a breakpoint on operation number n (as shown by 'listops').
info break -- List all the current breakpoints.
d <n> -- Delete the breakpoint on operation number n.
loc -- Show the current op code and location.
"""


class DebuggerInterface:
    """ Provides the interface to the debugger
    """
    def __init__(self):
        """ Initial setup
        """
        self.db_context = DebuggingContext()
        # Display the stack in hex
        self.hex_stack = False

    def set_noisy(self, boolean: bool) -> None:
        """ Set the noisy flag, set to False in unit tests to prevent printouts
        """
        self.db_context.noisy = boolean

    def print_status(self) -> None:
        """ Print out the current stack contents
        """
        if self.hex_stack:
            def as_hex(stack):
                return [f"0x{bytes(item).hex()}" for item in stack]
            print(f"stack(hex) = {as_hex(self.db_context.get_stack())}, "
                  f"altstack(hex) = {as_hex(self.db_context.get_altstack())}")
        else:
            print(f"stack(bytes) = {self.db_context.get_stack()}, "
                  f"altstack = {self.db_context.get_altstack()}")

    def load_script_file(self, fname: str) -> None:
        """ Load a script file
        """
        if not has_extension(fname, SCRIPT_EXTENSION):
            print(f"Wrong file extension (expected '.{SCRIPT_EXTENSION}'): {fname}")
            return
        self.db_context.load_script_file(fname)

    def has_script(self) -> bool:
        """ Return True if we have a script loaded.
        """
        return self.db_context.has_script()

    def run(self) -> None:
        """ Run a script from the start
        """
        if not self.has_script():
            print("No script loaded.")
            return
        self.db_context.reset()
        self.db_context.run()

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
            LOGGER.info("step: resetting script")
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
            print("Breakpoint location not set.")
            return

        try:
            n = int(user_input[1])
        except ValueError:
            print(f'Not an operation number: "{user_input[1]}"')
            return

        if not 0 <= n < self.db_context.get_number_of_operations():
            print(f"No operation {n}: this script has "
                  f"{self.db_context.get_number_of_operations()} operations "
                  f"(0 to {self.db_context.get_number_of_operations() - 1}).")
            return

        if self.db_context.breakpoints.add(n):
            if self.db_context.noisy:
                print(f"Added breakpoint at operation {n}.")
        else:
            print(f"Breakpoint already present at operation {n}.")

    def list_breakpoints(self) -> None:
        """ List all breakpoints
        """
        bps = self.db_context.breakpoints.get_all()
        if not bps:
            print("No breakpoints.")
            return
        for index, op_number in enumerate(bps):
            opcode = self.db_context.sf.instruction_offset[op_number][0]
            print(f"Breakpoint {index}: operation number {op_number}, op code {opcode}")

    def delete_breakpoint(self, user_input: List[str]) -> None:
        """ Delete the breakpoint on the given operation number
        """
        if len(user_input) < 2:
            print("Provide the operation number of the breakpoint to delete.")
            return
        try:
            n = int(user_input[1].strip())
        except ValueError:
            print(f'Not an operation number: "{user_input[1]}"')
            return
        if not self.db_context.breakpoints.delete(n):
            print(f"No breakpoint at operation {n}.")

    def execution_location(self) -> None:
        """ Report where execution has got to
        """
        if self.db_context.is_not_runable():
            print("Script has not been started.")
            return
        instruction_count = self.db_context.sf.instruction_count
        print(f"Instruction Number -> {instruction_count}")
        opcode = self.db_context.sf.current_opcode()
        if opcode is None:
            print("Instruction count is beyond the end of the script.")
        else:
            print(f"Op Code -> {opcode}")

    def process_input(self, user_input: List[str]) -> None:
        """ Process user input
        """
        if not user_input:
            return
        command = user_input[0]
        if command in ("h", "help"):
            print(HELP)
        elif command == "file":
            if len(user_input) < 2:
                print("The file command requires a filename.")
            else:
                self.load_script_file(user_input[1])
        elif command == "list":
            self.db_context.list()
        elif command == "listops":
            self.db_context.list_ops()
        elif command == "info":
            if len(user_input) > 1 and user_input[1] == "break":
                self.list_breakpoints()
            else:
                print('Unknown command "info". Did you mean "info break"?')
        elif command == "hex":
            self.hex_stack = True
        elif command == "dec":
            self.hex_stack = False
        elif command == "reset":
            self.reset()
        elif command in ("r", "run"):
            self.run()
        elif command in ("s", "step"):
            self.step()
        elif command == "c":
            self.continue_script()
        elif command == "b":
            self.add_breakpoint(user_input)
        elif command == "d":
            self.delete_breakpoint(user_input)
        elif command == "loc":
            self.execution_location()
        else:
            print(f'Unknown command "{command}".')

    def read_eval_print_loop(self) -> None:
        """ Main read-eval-print loop of the debugger.
        """
        while True:
            self.print_status()
            try:
                user_input = input("(gdb) ")
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'q' to quit.")
                continue
            split_input: List[str] = user_input.strip().split()
            if not split_input:
                continue
            if split_input[0] in ("q", "quit", "exit"):
                break
            self.process_input(split_input)

    def load_files_from_list(self, filenames: List[str]) -> None:
        """ Load each of the provided script files.
        """
        for fname in filenames:
            if has_extension(fname, SCRIPT_EXTENSION):
                self.load_script_file(fname)
            else:
                print(f"Unknown file type: {fname}")
                print(USAGE)
                sys.exit(1)
