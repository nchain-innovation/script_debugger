""" Command line interface to the debugger
"""
import argparse
import logging

from debug_interface import DebuggerInterface


def debugger_cmdline_parser():
    """ Parse the command line and call the debugger if there is a file to
        process.
    """
    parser = argparse.ArgumentParser(description="Debug bitcoin script.")
    parser.add_argument(
        "-v", "-verbose", "--verbose",
        dest="verbose",
        action="store_true",
        help="Provide extra debugging information."
    )
    parser.add_argument(
        "-file", "--file",
        dest="file",
        metavar="FILE",
        nargs="*",
        action="store",
        help="Provide the source file to debug."
    )
    args = parser.parse_args()

    # -verbose was previously accepted and then ignored; wire it to logging so
    # the LOGGER.info calls in the debugger actually appear.
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    print("Script debugger")
    print('For help, type "help".')

    dbif = DebuggerInterface()
    if args.file:
        dbif.load_files_from_list(args.file)

    dbif.read_eval_print_loop()


if __name__ == "__main__":
    debugger_cmdline_parser()
