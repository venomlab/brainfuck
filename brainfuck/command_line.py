import argparse
import sys

from . import Brainfuck
from .contrib.visitors.execution import ExecutionVisitorFactory
from .contrib.visitors.pyast import PyASTRootVisitor, PyASTVisitorFactory

parser = argparse.ArgumentParser()
parser.add_argument("-f", dest="file", required=False, default=None, type=str)
parser.add_argument("-oz", dest="optimize", required=False, default=False, action="store_true")
parser.add_argument("-py", dest="to_python", required=False, default=False, action="store_true")
parser.add_argument("-out", dest="out", required=False, default=None, type=str)


def main_cli():
    namespace = parser.parse_args()
    if namespace.file:
        with open(namespace.file, "r") as file:
            program = file.read()
    else:
        program = sys.stdin.readline()
    bf = Brainfuck.compile(program)
    if namespace.optimize:
        bf = bf.optimize()

    if namespace.to_python:
        visitor_factory = PyASTVisitorFactory()
        visitor: PyASTRootVisitor = bf.visit(visitor_factory)
        python_program = visitor.to_str()
        if namespace.out:
            with open(namespace.out, "w") as file:
                file.write(python_program)
        else:
            sys.stdout.write(python_program)
    else:
        visitor_factory = ExecutionVisitorFactory()
        bf.visit(visitor_factory)
