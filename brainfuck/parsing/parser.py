__all__ = [
    "parse_bf",
]

from .ast import Augment, GetChar, Loop, Move, PutChar, Root, Sequence
from .tokenizer import Token


def parse_bf(tokens: list[Token]) -> Root:
    stack = list()
    current = Sequence()
    for token in tokens:
        if token == Token.INC:
            current.nodes.append(Augment(1))
        elif token == Token.DEC:
            current.nodes.append(Augment(-1))
        elif token == Token.NEXT:
            current.nodes.append(Move(1))
        elif token == Token.PREV:
            current.nodes.append(Move(-1))
        elif token == Token.PUT_CHAR:
            current.nodes.append(PutChar())
        elif token == Token.GET_CHAR:
            current.nodes.append(GetChar())
        elif token == Token.SKIP_IF_NULL:
            loop = Loop()
            current.nodes.append(loop)
            stack.append(current)
            current = loop
        elif token == Token.BACK_IF_NOT_NULL:
            if stack:
                current = stack.pop()
            else:
                raise SyntaxError('Too much "]"')
    if stack:
        raise SyntaxError('Expected "]" got EOF')
    return Root(current)
