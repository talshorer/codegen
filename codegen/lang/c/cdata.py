#! /usr/bin/python3

from . import ccode


class IntLiteral(ccode.Expr):

    B_HEX = object()
    B_DEC = object()

    _BASE_TO_STR = {
        B_DEC: str,
        B_HEX: hex,
    }

    def __init__(self, value, base=B_DEC):
        ccode.Expr.__init__(self, self._BASE_TO_STR[base](value))


class StringLiteral(ccode.Expr):

    def __init__(self, s):
        ccode.Expr.__init__(self, "\"{}\"".format(s))
