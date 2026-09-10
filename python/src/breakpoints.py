""" Encapsulates debugger breakpoints
"""

from typing import List, Optional


class Breakpoints:
    """ Encapsulates the breakpoints used by the debugger.

        A breakpoint is an *operation number*: an index into
        `StackFrame.instruction_offset`, which is what `listops` prints and
        what the `b` command takes. `current_bp_index` is an index into
        `self.breakpoints` — the breakpoint the debugger is currently sitting
        on or heading towards. Confusing the two is the reason `hit()` used to
        compare an operation number against a list index.
    """
    def __init__(self):
        """ Initial setup
        """
        self.breakpoints: List[int] = []
        self.current_bp_index: int = 0

    def get_all(self) -> List[int]:
        """ Return all breakpoints, in ascending operation order
        """
        return self.breakpoints

    def add(self, op_number: int) -> bool:
        """ Add a breakpoint on operation `op_number`.
            Returns False if a breakpoint is already set there.
        """
        if op_number in self.breakpoints:
            return False
        self.breakpoints.append(op_number)
        # Keep the list ordered so get_next_breakpoint can walk it forwards.
        self.breakpoints.sort()
        return True

    def delete(self, op_number: int) -> bool:
        """ Delete the breakpoint on operation `op_number`.
            Returns False if there was no breakpoint there.
        """
        if op_number not in self.breakpoints:
            return False
        self.breakpoints.remove(op_number)
        self.current_bp_index = min(self.current_bp_index, len(self.breakpoints))
        return True

    def current(self) -> Optional[int]:
        """ Return the operation number of the breakpoint currently being
            tracked, or None if there is none.
        """
        if 0 <= self.current_bp_index < len(self.breakpoints):
            return self.breakpoints[self.current_bp_index]
        return None

    def hit(self, op_number: int) -> bool:
        """ Return True if `op_number` is the breakpoint currently being
            tracked.
        """
        return self.current() == op_number

    def get_current_bp_index(self) -> int:
        return self.current_bp_index

    def reset_all(self) -> None:
        """ Erase all breakpoints
        """
        self.breakpoints.clear()
        self.current_bp_index = 0

    def get_next_breakpoint(self, ip: int, inclusive: bool = True) -> Optional[int]:
        """ Return the next breakpoint at or after operation `ip`, advancing
            `current_bp_index` past any that have already been passed.

            `inclusive` selects whether a breakpoint exactly on `ip` counts:

            * `run` starts from a reset state and must honour a breakpoint on
              operation 0, so it passes inclusive=True.
            * `continue` is already sitting on a breakpoint and must move past
              it rather than stopping on it again, so it passes
              inclusive=False.

            Returns None when there is no further breakpoint.
        """
        self.current_bp_index = 0
        while self.current_bp_index < len(self.breakpoints):
            bp = self.breakpoints[self.current_bp_index]
            if bp > ip or (inclusive and bp == ip):
                return bp
            self.current_bp_index += 1
        return None
