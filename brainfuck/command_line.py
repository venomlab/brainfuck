import argparse
import sys

from . import Brainfuck
from .contrib import execute, to_python_code

parser = argparse.ArgumentParser()
input_group = parser.add_mutually_exclusive_group(required=True)
input_group.add_argument("-c", dest="cli", type=str)
input_group.add_argument("-f", dest="file", type=str)
parser.add_argument("-o", dest="optimize", required=False, default=False, action="store_true")
parser.add_argument("-py", dest="to_python", required=False, default=False, action="store_true")
parser.add_argument("-out", dest="out", required=False, default=None, type=str)


def main_cli() -> None:
    namespace = parser.parse_args()
    if namespace.file:
        with open(namespace.file, "r") as file:
            program = file.read()
    elif namespace.cli:
        program = namespace.cli
    bf = Brainfuck.compile(program)
    if namespace.optimize:
        bf = bf.optimize()

    if namespace.to_python:
        python_program = to_python_code(bf)
        if namespace.out:
            with open(namespace.out, "w") as file:
                file.write(python_program)
        else:
            sys.stdout.write(python_program)
    else:
        execute(bf)
