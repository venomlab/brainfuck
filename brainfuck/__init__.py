__all__ = [
    "Brainfuck",
]

from typing import cast

from .parsing.ast import Root, TVisitor, VisitorFactory
from .parsing.parser import parse_bf
from .parsing.tokenizer import tokenize_bf


class Brainfuck:
    def __init__(self, node: Root) -> None:
        self._node = node

    @classmethod
    def compile(cls, source: str) -> "Brainfuck":
        tokens = tokenize_bf(source)
        root_node = parse_bf(tokens)
        return cls(node=root_node)

    def optimize(self) -> "Brainfuck":
        return Brainfuck(self._node.optimize())

    def visit(self, visitor_factory: VisitorFactory[TVisitor]) -> TVisitor:
        self._node.assign_visitor(visitor_factory)
        self._node.visitor.visit(self._node)
        return cast(TVisitor, self._node.visitor)
