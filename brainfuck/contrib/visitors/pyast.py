__all__ = [
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
from typing import Dict, Generic, List, Tuple, Type, cast

from ...parsing.ast import (
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
        assign_byte_buffer = ast.Assign(
            targets=[ast.Name(self.ctx.buffer_var)],
            value=ast.Call(
                func=ast.Name(id=self.ctx.buffer_factory),
                args=[ast.Constant(self.ctx.bytes_amount)],
                keywords=[],
            ),
            lineno=0,
        )
        assign_index = ast.Assign(
            targets=[ast.Name(self.ctx.index_var)],
            value=ast.Constant(self.ctx.start_index),
            lineno=0,
        )
        sub_node = node.node
        sub_visitor = cast(PyASTVisitor, sub_node.visitor)
        sub_visitor.visit(sub_node)
        program_ast = sub_visitor.nodes
        self.root_node = ast.Module(
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

    def to_str(self) -> str:
        return ast.unparse(self.root_node)


class PyASTMoveVisitor(PyASTVisitor[Move]):
    def visit(self, node: Move) -> None:
        operation = ast.Sub() if node.value < 0 else ast.Add()
        self.nodes = [
            ast.AugAssign(
                target=ast.Name(self.ctx.index_var),
                op=operation,
                value=ast.Constant(abs(node.value)),
                lineno=0,
            )
        ]


class PyASTAugmentVisitor(PyASTVisitor[Augment]):
    def visit(self, node: Augment) -> None:
        operation = ast.Sub() if node.value < 0 else ast.Add()
        self.nodes = [
            ast.AugAssign(
                target=ast.Subscript(
                    value=ast.Name(self.ctx.buffer_var),
                    slice=ast.Name(self.ctx.index_var),
                ),
                op=operation,
                value=ast.Constant(abs(node.value)),
                lineno=0,
            )
        ]


class PyASTGetCharVisitor(PyASTVisitor[GetChar]):
    def visit(self, node: GetChar) -> None:
        subscript = ast.Subscript(
            value=ast.Name(self.ctx.buffer_var),
            slice=ast.Name(self.ctx.index_var),
        )
        read_function = ast.Call(func=ast.Name("input"), args=[], keywords=[])
        ord_function = ast.Call(func=ast.Name("ord"), args=[read_function], keywords=[])
        self.nodes = [
            ast.Assign(
                targets=[subscript],
                value=ord_function,
                lineno=0,
            )
        ]


class PyASTPutCharVisitor(PyASTVisitor[PutChar]):
    def visit(self, node: PutChar) -> None:
        subscript = ast.Subscript(
            value=ast.Name(self.ctx.buffer_var),
            slice=ast.Name(self.ctx.index_var),
        )
        chr_function = ast.Call(func=ast.Name("chr"), args=[subscript], keywords=[])
        print_function = ast.Call(
            func=ast.Name("print"),
            args=[chr_function],
            keywords=[ast.keyword(arg="end", value=ast.Constant(""))],
        )
        self.nodes = [ast.Expr(value=print_function)]


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
            sub_nodes = [ast.Pass()]
        self.nodes = [
            ast.While(
                test=ast.Compare(
                    left=ast.Subscript(
                        value=ast.Name(self.ctx.buffer_var),
                        slice=ast.Name(self.ctx.index_var),
                    ),
                    ops=[ast.NotEq()],
                    comparators=[ast.Constant(0)],
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
