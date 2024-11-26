""" Encapsulates debugger breakpoints
"""

from typing import Dict, List, Optional


class Breakpoints:
    """ Encapsulates breakpoints used by debugger
        The idea is to change it to just the list of OP_CODE locations
        
    """
    def __init__(self):
        """ Inital setup
        """
        #self.breakpoints: Dict[str, int] = {}
        #self.bpid: int = 0
        self.breakpoints: List[int] = []
        self.current_bp_index: int = 0

    #def get_all(self) -> Dict[str, int]:
    def get_all(self) -> List[int]:
        """ Return all breakpoints
        """
        return self.breakpoints

    def add(self, op_number: int) -> bool:
        """ Adds a breakpoint, returns the breakpoint id
            returns None if breakpoint already present
        """
        '''
        if self.hit(op_number):
            return None
        self.bpid += 1
        self.breakpoints[str(self.bpid)] = op_number
        return str(self.bpid)
        '''
        # breakpoint already set
        if op_number in self.breakpoints:
            return False
        self.breakpoints.append(op_number)
        # ensure the breakpoints are sort.
        self.breakpoints.sort()
        return True

    def delete(self, op_number: int) -> None:
        """ Delete breakpoint
        """
        # del self.breakpoints[bpid]
        if op_number in self.breakpoints:
            self.breakpoints.remove(op_number)


    def hit(self, ip_loc: int) -> bool:
        """ Returns true if hit a breakpoint
        """
        #return op_number in self.breakpoints.values()
        return ip_loc == self.current_bp_index

    def get_current_bp_index(self) -> int:
        return self.current_bp_index
    
    #def get_associated(self, op_number: int) -> str:
        """ Return the breakpoint associated with this op_number
        """
        #return list(self.breakpoints.keys())[list(self.breakpoints.values()).index(op_number)]

    def reset_all(self) -> None:
        """ Erase all breakpoints
        """
        self.breakpoints.clear()
        self.current_bp_index = 0

    # Function to track the next breakpoint
    def get_next_breakpoint(self, ip : int) -> Optional[int]:
        """
        Determines the next breakpoint based on the current program counter (PC).
        
        Args:
            ip (int): Current program counter.
            
        Returns:
            Optional[int]: The next breakpoint, or None if no breakpoints are left.
        """

        while self.current_bp_index < len(self.breakpoints) and ip >= self.breakpoints[self.current_bp_index]:
            self.current_bp_index += 1  # Move to the next breakpoint
    
        if self.current_bp_index < len(self.breakpoints):
            #return self.breakpoints[self.current_bp_index], self.current_bp_index
            return self.breakpoints[self.current_bp_index]
        #return None, self.current_bp_indexcurrent_index  # No more breakpoints
        return None # no more breakpoints
