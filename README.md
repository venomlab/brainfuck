# Brainfuck

Pure python brainfuck parser, interpreter Including optimizations, translation into python AST and python code

# Installation

```shell
pip install brainfuck-venomlab
```

# Usage

## From code

```python
from brainfuck import Brainfuck
from brainfuck.contrib import execute, to_python_ast, to_python_code

source_code = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++."

bf = Brainfuck.compile(source_code)
# Execute code directly
execute(bf)

# Optimize
bf = bf.optimize()

# Get python code
python_code = to_python_code(bf)  # type: str

# Get python AST
program = to_python_ast(bf)  # type: ast.AST
# Compile AST info code object with `exec` mode - it's module
executable = compile(program, "program.py", "exec")
# Either exec or eval
exec(executable)

```

## From command line

Execute brainfuck from *.bf file:

```shell
brainfuck -f examples/hw.bf
# Hello World!
```

Execute brainfuck from commandline:

```shell
brainfuck -c "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++."
# Hello
```

Translate brainfuck to python with `-py` flag:

```shell
brainfuck -py -c "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++."
# buffer = bytearray(30000)
# index = 0
# buffer[index] += 1
# buffer[index] += 1
# buffer[index] += 1
# ...
# print(chr(buffer[index]), end='')
```

Enable optimizations with `-o` flag:

```shell
brainfuck -py -o -c "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++."
# buffer = bytearray(30000)
# index = 0
# buffer[index] += 10
# ...
# buffer[index] += 3
# print(chr(buffer[index]), end='')
```

Write python output to file:

```shell
brainfuck -py -out "hw.py" -o -c "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++."
# file `hw.py` is created
```
