""" Utilities used by debugger
"""
import os
import logging
from typing import List, Optional, Union
from tx_engine import Script
from tx_engine.engine.op_code_names import OP_CODE_NAMES

LOGGER = logging.getLogger(__name__)

# Opcodes that open a block, and so indent everything after them.
BLOCK_OPEN = ("OP_IF", "OP_NOTIF", "OP_ELSE")
# Opcodes that close a block, and so are themselves printed outdented.
BLOCK_CLOSE = ("OP_ELSE", "OP_ENDIF")
INDENT_WIDTH = 2


def has_extension(fname: str, ext: str) -> bool:
    """ Return True if the file extension matches `ext` (given without a dot).
    """
    _, dot, actual = fname.rpartition(".")
    return bool(dot) and actual == ext


def change_directory(env_var: str) -> None:
    """ Change into the directory specified by the `env_var`
        environment variable.
    """
    try:
        source_dir = os.environ[env_var]
    except KeyError:
        pass
    else:
        LOGGER.info("change_directory %s", source_dir)
        os.chdir(source_dir)


def cmd_repr(cmd: Union[int, bytes]) -> Union[str, bytes]:
    """ Return a string (and bytes) representation of the command
        e.g. 0x5a -> OP_DUP
    """
    if isinstance(cmd, int):
        try:
            return OP_CODE_NAMES[cmd]
        except KeyError:
            return str(cmd)
    else:
        return cmd


def print_cmd(i: int, cmd: Union[int, bytes], indent: int = 0) -> int:
    """ Print the command and return the indent to use for the next one.
    """
    rendered = cmd_repr(cmd)
    if isinstance(rendered, str):
        if rendered in BLOCK_CLOSE:
            indent = max(0, indent - INDENT_WIDTH)
        print(f"{i}: {' ' * indent}{rendered}")
        if rendered in BLOCK_OPEN:
            indent += INDENT_WIDTH
    else:
        print(f"{i}: {' ' * indent}{int.from_bytes(rendered, byteorder='little')} (0x{rendered.hex()}, {rendered!r})")
    return indent


def format_cmds(script_str: str) -> str:
    """ Render a whitespace-separated script as numbered, indented lines.

        Only opcodes are numbered; data pushes are printed indented under the
        operation that follows them, matching the numbering the debugger uses
        for breakpoints.
    """
    op_code_names = set(OP_CODE_NAMES.values())
    formatted_script: List[str] = []
    indent = 0
    op_code_count = 0

    for token in script_str.split():
        if token not in op_code_names:
            # A data push: no operation number, indented under its operation.
            formatted_script.append(f"\t \t{' ' * (indent + INDENT_WIDTH)}{token}")
            continue
        if token in BLOCK_CLOSE:
            indent = max(0, indent - INDENT_WIDTH)
        formatted_script.append(f"\t{op_code_count}\t{' ' * indent}{token}")
        if token in BLOCK_OPEN:
            indent += INDENT_WIDTH
        op_code_count += 1

    return "\n".join(formatted_script)


def load_file(filename: str) -> Optional[Script]:
    """ Load and parse a script file.

        Returns None (after printing why) if the file is missing, unreadable,
        has the wrong extension, or does not parse.
    """
    if not has_extension(filename, "bs"):
        print(f"Not a bitcoin script file (expected a '.bs' extension): '{filename}'")
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            contents = [line.strip() for line in f]
    except OSError as e:
        print(e)
        return None

    try:
        return parse_script_new(contents)
    except Exception as e:
        print(f"Failed to parse '{filename}': {e}")
        return None


def parse_script_new(contents: List[str]) -> Script:
    """ Parse the provided lines into a single Script.
    """
    script = Script()
    for line in contents:
        if not line:
            continue
        script += Script.parse_string(line)
    return script


def list_full(script: Optional[Script]) -> None:
    """ Print the whole script, numbered and indented.
    """
    if script is None:
        print("No script loaded.")
        return
    print(format_cmds(script.to_debug_parser_string()))
