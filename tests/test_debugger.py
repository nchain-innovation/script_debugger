""" Tests of the debugger
"""
import unittest

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "python" / "src"))

from debug_interface import DebuggerInterface
from tx_engine import Script, Stack

EXAMPLES = REPO_ROOT / "examples"
EXAMPLE_ADD = str(EXAMPLES / "add.bs")
EXAMPLE_SWAP = str(EXAMPLES / "swap.bs")
EXAMPLE_PUSHDATA = str(EXAMPLES / "push_data.bs")
EXAMPLE_INTEGERS = str(EXAMPLES / "integer_to_script.bs")
EXAMPLE_LARGE_INTEGERS = str(EXAMPLES / "large_integer_test.bs")
EXAMPLE_PUSH_DATA_INTEGER_ADD = str(EXAMPLES / "large_data_push_integer_test.bs")
EXAMPLE_NESTED_IFS = str(EXAMPLES / "nested_ifs.bs")
EXAMPLE_SINGLE_OPIF = str(EXAMPLES / "single_opif.bs")


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
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [2]]))

        # Restarts from the beginning
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
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

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
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

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
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["s"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 1)

        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))
        # A completed run parks the instruction pointer at the end of the
        # script. It used to be left at 0, which made can_run() claim the
        # script was still runnable and re-executed it from the top.
        self.assertEqual(self.dbif.db_context.instruction_count, 3)

    def test_file_load_twice(self):
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["run"])
        self.assertIsNotNone(self.dbif.db_context.instruction_count)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))
        self.assertEqual(self.dbif.db_context.instruction_count, 3)

        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)

        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.instruction_count, 4)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1], [3], [2]]))

        # Having run to completion, reset and restart with 'step'.
        self.dbif.db_context.reset()
        self.dbif.process_input(["step"])
        self.assertEqual(self.dbif.db_context.instruction_count, 1)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[1]]))

    def test_push_data(self):
        self.dbif.process_input(["file", EXAMPLE_PUSHDATA])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_integer_addition(self):
        self.dbif.process_input(["file", EXAMPLE_INTEGERS])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_large_integer_addition(self):
        self.dbif.process_input(["file", EXAMPLE_LARGE_INTEGERS])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_push_and_integer_addition(self):
        self.dbif.process_input(["file", EXAMPLE_PUSH_DATA_INTEGER_ADD])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

        self.dbif.process_input(["reset"])
        self.dbif.process_input(["b", "3"])
        self.dbif.process_input(["b", "4"])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[0, 160, 114, 78, 24, 9], [0, 160, 114, 78, 24, 9]]))
        self.dbif.process_input(["c"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[0, 64, 229, 156, 48, 18], [0, 64, 229, 156, 48, 18]]))
        self.dbif.process_input(["c"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))


class RegressionTests(unittest.TestCase):
    """ One test per defect fixed, so they cannot come back silently.
    """
    def setUp(self):
        self.dbif = DebuggerInterface()
        self.dbif.set_noisy(False)

    def test_wrong_extension_is_rejected(self):
        """ The extension check used `not in ("bs")`, i.e. a substring test
            against the string "bs", so "foo.b" was accepted and then crashed.
        """
        self.dbif.load_script_file("foo.b")
        self.assertFalse(self.dbif.has_script())

    def test_missing_file_does_not_crash(self):
        self.dbif.process_input(["file", str(EXAMPLES / "does_not_exist.bs")])
        self.assertFalse(self.dbif.has_script())

    def test_bare_info_command(self):
        """ `info` on its own used to raise IndexError. """
        self.dbif.process_input(["info"])

    def test_commands_without_a_script(self):
        for cmd in (["run"], ["s"], ["c"], ["reset"], ["loc"], ["listops"],
                    ["b", "0"], ["d", "0"], ["info", "break"]):
            with self.subTest(cmd=cmd):
                self.dbif.process_input(cmd)

    def test_non_numeric_breakpoint_argument(self):
        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.dbif.process_input(["b", "two"])
        self.assertEqual(self.dbif.db_context.breakpoints.get_all(), [])

    def test_duplicate_breakpoint_is_reported_not_added(self):
        """ Breakpoints.add returns a bool; the caller tested it against None,
            so a duplicate was silently reported as added.
        """
        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.assertTrue(self.dbif.db_context.breakpoints.add(2))
        self.assertFalse(self.dbif.db_context.breakpoints.add(2))
        self.assertEqual(self.dbif.db_context.breakpoints.get_all(), [2])

    def test_delete_breakpoint_out_of_range(self):
        """ The bounds check used `>` instead of `>=`, so deleting the index
            one past the end raised IndexError.
        """
        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.dbif.process_input(["b", "1"])
        self.dbif.process_input(["d", "9"])
        self.dbif.process_input(["d", "-1"])
        self.assertEqual(self.dbif.db_context.breakpoints.get_all(), [1])
        self.dbif.process_input(["d", "1"])
        self.assertEqual(self.dbif.db_context.breakpoints.get_all(), [])

    def test_breakpoint_hit_compares_operation_not_list_index(self):
        """ Breakpoints.hit() compared the instruction pointer against
            current_bp_index (a list index) rather than the breakpoint value.
        """
        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.dbif.process_input(["b", "3"])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.instruction_count, 3)
        self.assertTrue(self.dbif.db_context.sf.hit_breakpoint())

    def test_breakpoint_on_first_operation_is_honoured(self):
        """ get_next_breakpoint skipped any breakpoint whose value equalled
            the current ip, so a breakpoint on operation 0 never fired and the
            script ran to completion.
        """
        self.dbif.process_input(["file", EXAMPLE_SWAP])
        self.dbif.process_input(["b", "0"])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.instruction_count, 0)
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([]))

    def test_run_to_end_then_step_does_not_re_execute(self):
        """ run() left instruction_count at 0, so can_run() stayed True and
            the next step re-ran the script from the top onto the finished
            stack.
        """
        self.dbif.process_input(["file", EXAMPLE_ADD])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))
        self.assertFalse(self.dbif.db_context.can_run())
        self.dbif.process_input(["s"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3]]))

    def test_empty_conditional_parses(self):
        """ The grammar required at least one statement inside OP_IF, so the
            shipped single_opif.bs example panicked the Rust parser.
        """
        self.dbif.process_input(["file", EXAMPLE_SINGLE_OPIF])
        self.assertTrue(self.dbif.has_script())
        self.assertEqual(
            [op for op, _ in self.dbif.db_context.sf.instruction_offset],
            ["OP_IF", "OP_ENDIF"])

    def test_nested_ifs_list_is_indented(self):
        """ format_cmds' indentation branches were unreachable, and two of
            them appended a literal "' ' * indent + f{op}" string.
        """
        self.dbif.process_input(["file", EXAMPLE_NESTED_IFS])
        from util import format_cmds
        rendered = format_cmds(
            Script(self.dbif.db_context.sf.context.cmds).to_debug_parser_string())
        self.assertNotIn("indent", rendered)

        # Lines are "\t<op number>\t<indent><opcode>".
        by_number = {}
        for line in rendered.splitlines():
            _, number, body = line.split("\t")
            by_number[number.strip()] = body

        def indent_of(op_number):
            body = by_number[str(op_number)]
            return len(body) - len(body.lstrip())

        # OP_1 OP_IF OP_2 OP_IF OP_3 OP_ELSE OP_8 OP_ENDIF OP_4 OP_ENDIF OP_5
        self.assertEqual(indent_of(0), 0)    # OP_1
        self.assertEqual(indent_of(1), 0)    # OP_IF
        self.assertEqual(indent_of(2), 2)    # OP_2, one level in
        self.assertEqual(indent_of(3), 2)    # nested OP_IF
        self.assertEqual(indent_of(4), 4)    # OP_3, two levels in
        self.assertEqual(indent_of(5), 2)    # OP_ELSE, outdented
        self.assertEqual(indent_of(6), 4)    # OP_8
        self.assertEqual(indent_of(7), 2)    # inner OP_ENDIF
        self.assertEqual(indent_of(9), 0)    # outer OP_ENDIF
        self.assertEqual(indent_of(10), 0)   # OP_5

    def test_run_evaluates_conditionals_correctly(self):
        """ Whole-script evaluation takes the right branches. """
        self.dbif.process_input(["file", EXAMPLE_NESTED_IFS])
        self.dbif.process_input(["run"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3], [4], [5]]))

    @unittest.expectedFailure
    def test_stepping_through_a_conditional(self):
        """ KNOWN UNFIXED DEFECT.

            Stepping executes one operation per tx_engine evaluate_core call,
            bracketed by ip_start/ip_limit. tx_engine's evaluator is stateless
            across those calls, so a lone OP_IF fails with "ENDIF missing" and
            no branch state survives to the next step: both arms of the
            conditional end up executing. Stepping gives
            Stack([1],[2],[3],[8],[4],[5]) where "run" correctly gives
            Stack([3],[4],[5]).

            Fixing this needs conditional state carried across steps, either
            in tx_engine or tracked by the debugger. That is a design change,
            not a bug fix, so it is recorded here rather than papered over.
        """
        self.dbif.process_input(["file", EXAMPLE_NESTED_IFS])
        while self.dbif.db_context.can_run():
            self.dbif.process_input(["s"])
        self.assertEqual(self.dbif.db_context.get_stack(), Stack([[3], [4], [5]]))

    def test_malformed_script_raises_value_error_not_panic(self):
        from bitcoin_script_parser import parse_script
        for bad in ("OP_ENDIF", "OP_DUPLICATE", "0xaabbc", "OP_IF OP_1"):
            with self.subTest(script=bad):
                with self.assertRaises(ValueError):
                    parse_script(bad)


if __name__ == "__main__":
    unittest.main()
