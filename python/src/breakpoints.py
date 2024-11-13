""" Encapsulates debugger breakpoints
"""

from typing import Dict, Optional


class Breakpoints:
    """ Encapsulates breakpoints used by debugger
    """
    def __init__(self):
        """ Inital setup
        """
        self.breakpoints: Dict[str, int] = {}
        self.bpid: int = 0

    def get_all(self) -> Dict[str, int]:
        """ Return all breakpoints
        """
        return self.breakpoints

    def add(self, op_number: int) -> Optional[str]:
        """ Adds a breakpoint, returns the breakpoint id
            returns None if breakpoint already present
        """
        if self.hit(op_number):
            return None
        self.bpid += 1
        self.breakpoints[str(self.bpid)] = op_number
        return str(self.bpid)

    def delete(self, bpid) -> None:
        """ Delete breakpoint
        """
        del self.breakpoints[bpid]

    def hit(self, op_number: int) -> bool:
        """ Returns true if hit a breakpoint
        """
        return op_number in self.breakpoints.values()

    def get_associated(self, op_number: int) -> str:
        """ Return the breakpoint associated with this op_number
        """
        return list(self.breakpoints.keys())[list(self.breakpoints.values()).index(op_number)]

    def reset_all(self) -> None:
        """ Erase all breakpoints
        """
        self.breakpoints.clear()
        self.bpid = 0

    def get_next_breakpoint(self, ip: int) -> None | int:
        """ Based on the current ip determine the next breakpoint
        """
        if len(self.breakpoints) == 0:
            return None
        # Get first breakpoint (greater than current ip)
        bps = list(self.breakpoints.values())
        # Sort in ascending order
        bps.sort()
        for bp in bps:
            if bp > ip:
                return bp
        return None
