__all__ = [
    "ExecutionVisitorFactory",
    "ExecutionMoveVisitor",
    "ExecutionRootVisitor",
    "ExecutionAugmentVisitor",
    "ExecutionLoopVisitor",
    "ExecutionSequenceVisitor",
    "ExecutionGetCharVisitor",
    "ExecutionPutCharVisitor",
    "ExecutionVisitor",
    "ExecutionContext",
]

import sys
from typing import Dict, Generic, TextIO, Type

from ...parsing.ast import (
    Augment,
    GetChar,
    Loop,
    Move,
    NodeType,
    PutChar,
    Root,
    Sequence,
    TNode,
    Visitor,
    VisitorFactory,
)


class ExecutionContext:
    def __init__(self, inp: TextIO = sys.stdin, out: TextIO = sys.stdout) -> None:
        self.out = out
        self.inp = inp
        self.buffer = bytearray(30000)
        self.index = 0

    def read(self) -> int:
        return ord(self.inp.read(1))

    def write(self, value: int) -> None:
        self.out.write(chr(value))

    def _get_current(self) -> int:
        return self.buffer[self.index]

    def _set_current(self, value: int) -> None:
        self.buffer[self.index] = value

    current = property(_get_current, _set_current)


class ExecutionVisitor(Generic[TNode], Visitor[TNode]):
    def __init__(self, ctx: ExecutionContext) -> None:
        self.ctx = ctx


class ExecutionRootVisitor(ExecutionVisitor[Root]):
    def visit(self, node: Root) -> None:
        sub_node = node.node
        sub_node.visitor.visit(sub_node)


class ExecutionMoveVisitor(ExecutionVisitor[Move]):
    def visit(self, node: Move) -> None:
        self.ctx.index += node.value


class ExecutionAugmentVisitor(ExecutionVisitor[Augment]):
    def visit(self, node: Augment) -> None:
        self.ctx.current += node.value


class ExecutionGetCharVisitor(ExecutionVisitor[GetChar]):
    def visit(self, node: GetChar) -> None:
        self.ctx.current = self.ctx.read()


class ExecutionPutCharVisitor(ExecutionVisitor[PutChar]):
    def visit(self, node: PutChar) -> None:
        self.ctx.write(self.ctx.current)


class ExecutionSequenceVisitor(ExecutionVisitor[Sequence]):
    def visit(self, node: Sequence) -> None:
        for n in node.nodes:
            n.visitor.visit(n)


class ExecutionLoopVisitor(ExecutionVisitor[Loop]):
    def visit(self, node: Loop) -> None:
        while self.ctx.current != 0:
            for n in node.nodes:
                n.visitor.visit(n)


class ExecutionVisitorFactory(VisitorFactory[ExecutionVisitor]):
    MAPPING: Dict[NodeType, Type[ExecutionVisitor]] = {
        NodeType.AUGMENT: ExecutionAugmentVisitor,
        NodeType.MOVE: ExecutionMoveVisitor,
        NodeType.GET_CHAR: ExecutionGetCharVisitor,
        NodeType.PUT_CHAR: ExecutionPutCharVisitor,
        NodeType.SEQUENCE: ExecutionSequenceVisitor,
        NodeType.LOOP: ExecutionLoopVisitor,
        NodeType.ROOT: ExecutionRootVisitor,
    }

    def __init__(self) -> None:
        self.ctx = ExecutionContext()

    def get_for_node(self, node: TNode) -> ExecutionVisitor[TNode]:
        return self.MAPPING[node.node_type](self.ctx)
