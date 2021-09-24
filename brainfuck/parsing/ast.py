__all__ = [
    "TNode",
    "TVisitor",
    "Visitor",
    "VisitorFactory",
    "Node",
    "Root",
    "Move",
    "Augment",
    "GetChar",
    "PutChar",
    "Sequence",
    "Loop",
    "NodeType",
]

import enum
from typing import Generic, TypeVar

TNode = TypeVar("TNode", bound="Node")
TVisitor = TypeVar("TVisitor", bound="Visitor")


class Visitor(Generic[TNode]):
    def visit(self, node: TNode) -> None:
        raise NotImplementedError


class VisitorFactory(Generic[TVisitor]):
    def get_for_node(self, node: TNode) -> TVisitor:
        raise NotImplementedError


class Node:
    visitor: Visitor

    @property
    def node_type(self) -> "NodeType":
        return NodeType(self.__class__.__name__)

    def assign_visitor(self, visitor_factory: VisitorFactory) -> None:
        self.visitor = visitor_factory.get_for_node(self)

    def optimize(self) -> "Node":
        raise NotImplementedError

    def _merge(self, other: "Node") -> "Node":
        raise ValueError()

    def _skip(self) -> bool:
        return False


class Root(Node):
    def __init__(self, node: Node) -> None:
        self.node = node

    def optimize(self) -> "Root":
        return Root(self.node.optimize())

    def assign_visitor(self, visitor_factory: VisitorFactory) -> None:
        super().assign_visitor(visitor_factory)
        self.node.assign_visitor(visitor_factory)


class PutChar(Node):
    def optimize(self) -> "Node":
        return self


class GetChar(Node):
    def optimize(self) -> "Node":
        return self


class Move(Node):
    """
    This is optimized variant of next/prev
    """

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def optimize(self) -> "Node":
        return self

    def _merge(self, other: "Node") -> "Node":
        if isinstance(other, Move):
            return Move(self.value + other.value)
        else:
            return super()._merge(other)

    def _skip(self) -> bool:
        return self.value == 0


class Augment(Node):
    """
    This is optimized variant of inc/dec
    """

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def optimize(self) -> "Node":
        return self

    def _merge(self, other: "Node") -> "Node":
        if isinstance(other, Augment):
            return Augment(self.value + other.value)
        else:
            return super()._merge(other)

    def _skip(self) -> bool:
        return self.value == 0


class Sequence(Node):
    def __init__(self) -> None:
        self.nodes: list[Node] = list()

    def assign_visitor(self, visitor_factory: VisitorFactory) -> None:
        super().assign_visitor(visitor_factory)
        for n in self.nodes:
            n.assign_visitor(visitor_factory)

    def optimize(self) -> "Node":
        obj = type(self)()
        obj.nodes = self._optimize_nodes()
        return obj

    def _optimize_nodes(self) -> list[Node]:
        current = None
        nodes = []
        for n in self.nodes:
            n = n.optimize()
            if not current:
                current = n
            else:
                try:
                    current = current._merge(n)
                except ValueError:
                    if not current._skip():
                        nodes.append(current)
                    current = n
        else:
            if current and not current._skip():
                nodes.append(current)
        return nodes


class Loop(Sequence):
    pass


class NodeType(str, enum.Enum):
    MOVE = Move.__name__
    AUGMENT = Augment.__name__
    GET_CHAR = GetChar.__name__
    PUT_CHAR = PutChar.__name__
    SEQUENCE = Sequence.__name__
    LOOP = Loop.__name__
    ROOT = Root.__name__
