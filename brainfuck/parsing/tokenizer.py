__all__ = [
    "Token",
    "tokenize_bf",
]

import enum


class Token(str, enum.Enum):
    NEXT = ">"
    PREV = "<"
    INC = "+"
    DEC = "-"
    PUT_CHAR = "."
    GET_CHAR = ","
    SKIP_IF_NULL = "["
    BACK_IF_NOT_NULL = "]"
    SPACE = " "
    LINEBREAK = "\n"
    CARET_RETURN = "\r"


def tokenize_bf(source: str) -> list[Token]:
    tokens = []
    for symbol in source:
        tokens.append(Token(symbol))
    return tokens
