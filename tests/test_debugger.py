""" Tests of the debugger
"""
import unittest

import sys
sys.path.append("../python/src")

from debug_interface import DebuggerInterface
from tx_engine import Stack
import bitcoin_script_parser

EXAMPLE_ADD = "../examples/add.bs"
EXAMPLE_SWAP = "../examples/swap.bs"
EXAMPLE_PUSHDATA = "../examples/push_data.bs"
EXAMPLE_INTEGERS = "../examples/integer_to_script.bs"
EXAMPLE_LARGE_INTEGERS= "../examples/large_integer_test.bs"
EXAMPLE_PUSH_DATA_INTEGER_ADD = "../examples/large_data_push_integer_test.bs"

class DebuggerTests(unittest.TestCase):
    """ Tests of the debugger
    """
    def setUp(self):
        self.dbif = DebuggerInterface()
        self.dbif.set_noisy(False)

    def test_breakpoint(self):
        self.dbif.process_input(["file", EXAMPLE_SWAP])

        self.dbif.process_input(["b", "2"])


        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.ip, 2)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1],[2]]))

        # Restarts from the begining
        self.dbif.process_input(["reset"])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.ip, 2)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [2]]))
        # Continues from current position
        self.dbif.process_input(["c"])
        self.assertEqual(self.dbif.db_context.ip, len(self.dbif.db_context.sf.instruction_offset))
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [3], [2]]))

    def test_file(self):
        """ Simple file load
        """
        self.assertFalse(self.dbif.db_context.has_script())
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertTrue(self.dbif.db_context.has_script())

    def test_run(self):
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["run"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))

    def test_step(self):
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertEqual(self.dbif.db_context.instruction_count,0)

        self.dbif.process_input(["s"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 1)

        self.dbif.process_input(["step"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [2]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 2)

        self.dbif.process_input(["step"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 3)

    def test_step_and_reset(self):
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertEqual(self.dbif.db_context.instruction_count,0)

        self.dbif.process_input(["s"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 1)

        self.dbif.process_input(["step"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [2]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 2)

        self.dbif.process_input(["reset"])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["step"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 1)

        self.dbif.process_input(["step"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [2]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 2)

    def test_step_and_run(self):
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertEqual(self.dbif.db_context.instruction_count,0)

        self.dbif.process_input(["s"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 1)

        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

    def test_file_load_twice(self):
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertEqual(self.dbif.db_context.instruction_count,0)

        self.dbif.process_input(["run"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1],[3],[2]]))

        # not sure what this is trying to achieve .. so the script runs to completion
        # and the restart with the 'step'
        self.dbif.db_context.reset()
        self.dbif.process_input(["step"])
        self.assertEqual(self.dbif.db_context.instruction_count, 1)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))

    def test_push_data(self):
        self.dbif.process_input(["file", EXAMPLE_PUSHDATA])
        self.dbif.process_input(["run"])
        #print(self.dbif.db_context.get_stack())
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_integer_addition(self):
        self.dbif.process_input(["file", EXAMPLE_INTEGERS])
        self.dbif.process_input(["run"])
        #print(self.dbif.db_context.get_stack())
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_large_integer_addition(self):
        self.dbif.process_input(["file", EXAMPLE_LARGE_INTEGERS])
        self.dbif.process_input(["run"])
        #print(self.dbif.db_context.get_stack())
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_push_and_integer_addition(self):
        self.dbif.process_input(["file", EXAMPLE_PUSH_DATA_INTEGER_ADD])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(),Stack([]))

        self.dbif.process_input(["reset"])
        self.dbif.process_input(["b", "3"])
        self.dbif.process_input(["b", "4"])
        # test breakpoints are set.
        self.dbif.process_input(["run"])
        print(f'{self.dbif.db_context.get_stack()}')
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[0, 160, 114, 78, 24, 9], [0, 160, 114, 78, 24, 9]]))
        self.dbif.process_input(["c"])
        self.assertEqual(self.dbif.db_context.get_stack(),  Stack([[0, 64, 229, 156, 48, 18], [0, 64, 229, 156, 48, 18]]))
        self.dbif.process_input(["c"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))
        
if __name__ == "__main__":
    unittest.main()
