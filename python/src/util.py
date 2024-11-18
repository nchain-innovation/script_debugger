""" Utilities used by debugger
"""
import os
import logging
from typing import List, Union
from tx_engine import Script
from tx_engine.engine.op_code_names import OP_CODE_NAMES

LOGGER = logging.getLogger(__name__)

def has_extension(fname: str, ext: str) -> bool:
    """ Return true if the file extension matches.
    """
    file_name = fname.split(".")
    if len(file_name) > 1:
        if file_name[-1] == ext:
            return True
    else:
        print(f"No file extension provided '{fname}'")
    return False

def change_directory(env_var: str) -> None:
    """ Change into the directory specified by the `env_var`
        environment variable.
    """
    try:
        source_dir = os.environ[env_var]
    except KeyError:
        pass
    else:
        LOGGER.info(f"change_directory {source_dir}")
        os.chdir(source_dir)

def cmd_repr(cmd: int) -> Union[str, bytes]:
    """ Return a string (and bytes) representation of the command
        e.g. 0x5 -> OP_10
    """
    if isinstance(cmd, int):
        try:
            return OP_CODE_NAMES[cmd]
        except KeyError:
            return str(cmd)
    else:
        return cmd


def print_cmd(i: int, cmd, indent: int = 0) -> int:
    """ Prints the command and manages the indent
    """
    cmd = cmd_repr(cmd)
    if isinstance(cmd, str):
        if cmd in ("OP_ELSE", "OP_ENDIF"):
            indent -= 2
        print(f"{i}: {' ' * indent}{cmd}")
        if cmd in ("OP_IF", "OP_NOTIF", "OP_ELSE"):
            indent += 2
    else:
        print(f"{i}: {' ' * indent}{int.from_bytes(cmd, byteorder='little')} (0x{cmd.hex()}, {cmd})")
    return indent

def format_cmds(script_str: str) -> str:
    lines = script_str.split() # split by whitespaces
    formatted_script: List = []
    indent: int = 0
    op_code_count: int = 0
    for op in lines:
        # add op_code number
        if op in OP_CODE_NAMES.values():
            formatted_script.append(f'{op_code_count}\t' + f'{op}')
            op_code_count += 1
        # deal with indentation
        elif op in ["OP_IF", "OP_NOTIF"]:
            f'{op_code_count} {op}'
            formatted_script.append(f'{op_code_count}\t' + " ' ' * indent + f{op}")
            op_code_count += 1
            indent += 2
        elif op == "OP_ELSE":
            # decrease before printing, OP_ELSE, increase afterwards
            indent -= 2
            formatted_script.append(f'{op_code_count}\t' + f" ' ' * indent + {op}")
            indent += 2
            op_code_count += 1
        elif op == "OP_ENDIF":
            # decreate indentation befre printing
            indent -= 2
            formatted_script.append(f'{op_code_count}\t' + f" ' ' * indent + {op}")
            op_code_count += 1
        else:
            # just print
            formatted_script.append('\t' + ' ' * indent + op)
            
    return '\n'.join(f'\t{item}' for item in formatted_script)


def load_file(filename: str) -> Script:
        """ Load loaded file, but don't parse it
        """
        try:
            # load it
            with open(filename, "r", encoding="utf-8") as f:
                # contents = f.readlines()
                contents = [line.strip() for line in f.readlines()]
        except FileNotFoundError as e:
            print(e)
        else:
            if has_extension(filename, "bs"):
                return parse_script_new(contents)


def parse_script_new(contents: List[str]) -> Script:
    """ Parse provided contents
    """
    script = Script() 
    if contents:
    # Initialize an empty script or container to hold the full script
        # Iterate through each line and process it, adding each part to the script
        for line in contents:
            #print(f'{line}')
            tmp_script = Script.parse_string(line)
            script += tmp_script

    # set up the instruction offsets
    #script_str = script.to_string()
    #print(f'parse_script_new -> {script_str}')
    return script
    #self.instruction_offset =  bitcoin_script_parser.bitcoin_script_parser.parse_script(self.script.to_string())


def list_full(script: Script) -> None:
    if script:
        script_str: str = script.to_debug_parser_string()
        print(format_cmds(script_str))
