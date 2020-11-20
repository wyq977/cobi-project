import os
from os import SEEK_END
import platform
import multiprocessing
import subprocess
import sys

default_num_threads = multiprocessing.cpu_count()

# TODO: use colorama instead like taichi
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def get_os_name():
    name = platform.platform()
    # in python 3.8, platform.platform() uses mac_ver() on macOS
    # it will return 'macOS-XXXX' instead of 'Darwin-XXXX'
    if name.lower().startswith("darwin") or name.lower().startswith("macos"):
        return "osx"
    elif name.lower().startswith("windows"):
        return "win"
    elif name.lower().startswith("linux"):
        return "linux"
    assert False, "Unknown platform name %s" % name


def check_exists(src):
    if not os.path.exists(src):
        raise FileNotFoundError(f'File "{src}" not exist.')


def readlast(filename):
    # not pythonic, only works on unix platform
    # https://stackoverflow.com/questions/3346430/what-is-the-most-efficient-way-to-get-first-and-last-line-of-a-text-file # too complicated
    if get_os_name() == "win":
        with open(filename, "r") as f:
            res = f.readlines()[-1]
    else:
        res = subprocess.check_output(["tail", "-1", filename]).decode(
            sys.stdout.encoding
        )

    return res


# The builtin `warnings` module is unreliable as it may be supressed
# by other packages, e.g. IPython.
def warning(msg, type=UserWarning, stacklevel=1):
    import traceback

    s = traceback.extract_stack()[:-stacklevel]
    raw = "".join(traceback.format_list(s))
    print(f"{bcolors.WARNING}{bcolors.BOLD}{type.__name__}: {msg}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}{bcolors.BOLD}\n{raw}{bcolors.ENDC}")


__all__ = [
    "warning",
    "readlast",
    "check_exists",
    "get_os_name",
]
