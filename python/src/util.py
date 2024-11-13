""" Utilities used by debugger
"""
import os
import logging
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
