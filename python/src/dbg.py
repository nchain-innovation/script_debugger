""" Command line interface to the debugger
"""
import argparse

from debug_interface import DebuggerInterface


def debugger_cmdline_parser():
    """ Parse the command line and call debugger if there is a file to process
    """
    parser = argparse.ArgumentParser(description="Debug bitcoin script.")
    parser.add_argument(
        "-verbose", "-v",
        action="store_true",
        help="Provide extra debugging information."
    )
    parser.add_argument(
        "-file",
        metavar="FILE",
        nargs="*",
        action="store",
        help="Provide the source file to debug."
    )
    args = parser.parse_args()

    print("Script debugger")
    print('For help, type "help".')

    dbif = DebuggerInterface()
    if args.file:
        dbif.load_files_from_list(args.file)

    dbif.read_eval_print_loop()


if __name__ == "__main__":
    debugger_cmdline_parser()
