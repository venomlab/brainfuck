__all__ = [
    "to_python_ast",
    "to_python_code",
    "PyASTVisitorFactory",
    "PyASTRootVisitor",
    "PyASTMoveVisitor",
    "PyASTLoopVisitor",
    "PyASTAugmentVisitor",
    "PyASTSequenceVisitor",
    "PyASTGetCharVisitor",
    "PyASTPutCharVisitor",
    "PyASTVisitor",
    "PyASTContext",
]

import ast
import itertools
from typing import Dict, Generic, List, Tuple, Type, TypeVar, cast

from .. import Brainfuck
from ..parsing.ast import (
    Augment,
    GetChar,
    Loop,
    Move,
    Node,
    NodeType,
    PutChar,
    Root,
    Sequence,
    TNode,
    Visitor,
    VisitorFactory,
)

_AST = TypeVar(
    "_AST",
    ast.Name,
    ast.Module,
    ast.Expr,
    ast.Add,
    ast.Sub,
    ast.Constant,
    ast.While,
    ast.Pass,
    ast.Call,
    ast.Assign,
    ast.AugAssign,
)


def to_python_ast(bf: Brainfuck) -> ast.AST:
    visitor_factory = PyASTVisitorFactory()
    visitor = cast(PyASTRootVisitor, bf.visit(visitor_factory))
    return visitor.root_node


def to_python_code(bf: Brainfuck) -> str:
    return ast.unparse(to_python_ast(bf))


def _ast(ast_type: Type[_AST], *args, **kwargs) -> _AST:
    if ast_type in [ast.Name, ast.Subscript]:
        kwargs.setdefault("ctx", ast.Load())
    kwargs.setdefault("lineno", 0)
    kwargs.setdefault("col_offset", 0)
    return ast_type(*args, **kwargs)


class PyASTContext:
    def __init__(self) -> None:
        self.buffer_var = "buffer"
        self.index_var = "index"
        self.buffer_factory = "bytearray"
        self.start_index = 0
        self.bytes_amount = 30000


class PyASTVisitor(Generic[TNode], Visitor[TNode]):
    nodes: List[ast.AST]

    def __init__(self, ctx: PyASTContext) -> None:
        self.ctx = ctx
        self.nodes = []


class PyASTRootVisitor(PyASTVisitor[Root]):
    root_node: ast.AST

    def visit(self, node: Root) -> None:
        assign_byte_buffer = _ast(
            ast.Assign,
            targets=[_ast(ast.Name, self.ctx.buffer_var, ctx=ast.Store())],
            value=_ast(
                ast.Call,
                func=_ast(ast.Name, self.ctx.buffer_factory),
                args=[_ast(ast.Constant, self.ctx.bytes_amount)],
                keywords=[],
            ),
        )
        assign_index = _ast(
            ast.Assign,
            targets=[_ast(ast.Name, self.ctx.index_var, ctx=ast.Store())],
            value=_ast(ast.Constant, self.ctx.start_index),
        )
        sub_node = node.node
        sub_visitor = cast(PyASTVisitor, sub_node.visitor)
        sub_visitor.visit(sub_node)
        program_ast = sub_visitor.nodes
        self.root_node = _ast(
            ast.Module,
            body=[
                assign_byte_buffer,
                assign_index,
                *program_ast,
            ],
            type_ignores=[],
        )
        self.nodes = [
            self.root_node,
        ]


class PyASTMoveVisitor(PyASTVisitor[Move]):
    def visit(self, node: Move) -> None:
        operation = _ast(ast.Sub, lineno=0, col_offset=0) if node.value < 0 else _ast(ast.Add, lineno=0, col_offset=0)
        self.nodes = [
            _ast(
                ast.AugAssign,
                target=_ast(ast.Name, self.ctx.index_var, ctx=ast.Store()),
                op=operation,
                value=_ast(ast.Constant, abs(node.value)),
            )
        ]


class PyASTAugmentVisitor(PyASTVisitor[Augment]):
    def visit(self, node: Augment) -> None:
        operation = _ast(ast.Sub, lineno=0, col_offset=0) if node.value < 0 else _ast(ast.Add, lineno=0, col_offset=0)
        self.nodes = [
            _ast(
                ast.AugAssign,
                target=_ast(
                    ast.Subscript,
                    value=_ast(ast.Name, self.ctx.buffer_var),
                    slice=_ast(ast.Name, self.ctx.index_var),
                    ctx=ast.Store(),
                ),
                op=operation,
                value=_ast(ast.Constant, abs(node.value)),
            )
        ]


class PyASTGetCharVisitor(PyASTVisitor[GetChar]):
    def visit(self, node: GetChar) -> None:
        subscript = _ast(
            ast.Subscript,
            value=_ast(ast.Name, self.ctx.buffer_var),
            slice=_ast(ast.Name, self.ctx.index_var),
        )
        read_function = _ast(ast.Call, func=_ast(ast.Name, "input"), args=[], keywords=[])
        ord_function = _ast(ast.Call, func=_ast(ast.Name, "ord"), args=[read_function], keywords=[])
        self.nodes = [
            _ast(
                ast.Assign,
                targets=[subscript],
                value=ord_function,
            )
        ]


class PyASTPutCharVisitor(PyASTVisitor[PutChar]):
    def visit(self, node: PutChar) -> None:
        subscript = _ast(
            ast.Subscript,
            value=_ast(ast.Name, self.ctx.buffer_var),
            slice=_ast(ast.Name, self.ctx.index_var),
        )
        chr_function = _ast(ast.Call, func=_ast(ast.Name, "chr"), args=[subscript], keywords=[])
        print_function = _ast(
            ast.Call,
            func=_ast(ast.Name, "print"),
            args=[chr_function],
            keywords=[_ast(ast.keyword, arg="end", value=_ast(ast.Constant, ""))],
        )
        self.nodes = [_ast(ast.Expr, value=print_function)]


class PyASTSequenceVisitor(PyASTVisitor[Sequence]):
    def visit(self, node: Sequence) -> None:
        visitors = cast(List[Tuple[Node, PyASTVisitor]], [(n, n.visitor) for n in node.nodes])
        for n, v in visitors:
            v.visit(n)
        self.nodes = list(itertools.chain.from_iterable(v.nodes for n, v in visitors))


class PyASTLoopVisitor(PyASTVisitor[Loop]):
    def visit(self, node: Loop) -> None:
        visitors = cast(List[Tuple[Node, PyASTVisitor]], [(n, n.visitor) for n in node.nodes])
        for n, v in visitors:
            v.visit(n)
        sub_nodes = list(itertools.chain.from_iterable(v.nodes for n, v in visitors))
        if not sub_nodes:
            sub_nodes = [_ast(ast.Pass)]
        self.nodes = [
            _ast(
                ast.While,
                test=_ast(
                    ast.Compare,
                    left=_ast(
                        ast.Subscript,
                        value=_ast(ast.Name, self.ctx.buffer_var),
                        slice=_ast(ast.Name, self.ctx.index_var),
                    ),
                    ops=[_ast(ast.NotEq)],
                    comparators=[_ast(ast.Constant, 0)],
                ),
                body=sub_nodes,
                orelse=[],
            )
        ]


class PyASTVisitorFactory(VisitorFactory[PyASTVisitor]):
    MAPPING: Dict[NodeType, Type[PyASTVisitor]] = {
        NodeType.AUGMENT: PyASTAugmentVisitor,
        NodeType.MOVE: PyASTMoveVisitor,
        NodeType.GET_CHAR: PyASTGetCharVisitor,
        NodeType.PUT_CHAR: PyASTPutCharVisitor,
        NodeType.SEQUENCE: PyASTSequenceVisitor,
        NodeType.LOOP: PyASTLoopVisitor,
        NodeType.ROOT: PyASTRootVisitor,
    }

    def __init__(self) -> None:
        self.ctx = PyASTContext()

    def get_for_node(self, node: TNode) -> PyASTVisitor[TNode]:
        return self.MAPPING[node.node_type](self.ctx)
