#! /usr/bin/python3

from codegen.core.code import Code


def _cls_repr(cls):
    return "{}.{}".format(cls.__module__, cls.__name__)


class Expr(Code):

    def __init__(self, expr):
        self.expr = expr

    def _act(self, source):
        source.write(self.expr)

    def __repr__(self):
        return "{}({!r})".format(_cls_repr(type(self)), self.expr)

    @classmethod
    def exprs_from_text(cls, text):
        return [cls(part.strip()) for part in text.split(";") if part]


class Block(Code):

    def __init__(self, code=None):
        if code is None:
            code = []
        self.code = code

    def add_code(self, code):
        self.code.append(code)

    def _act(self, source):
        source.writeline("{")
        source.indent()
        for part in self.code:
            part._act(source)
            if isinstance(part, Expr):
                source.writeline(";")
        source.dedent()
        source.writeline("}")

    def __repr__(self):
        return "{}({!r})".format(_cls_repr(type(self)), self.code)


class IfBlock(Block):

    MAGIC_WORD = "if"

    def __init__(self, cond, code=None):
        self.cond = cond
        Block.__init__(self, code)

    def _act(self, source):
        source.write("{} (".format(self.MAGIC_WORD))
        self.cond._act(source)
        source.write(") ")
        Block._act(self, source)

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            _cls_repr(type(self)),
            self.decl,
            self.code,
        )


class Func(Block):

    def __init__(self, decl, code=None):
        self.decl = decl
        Block.__init__(self, code)

    def _act(self, source):
        source.writeline(str(self.decl))
        Block._act(self, source)

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            _cls_repr(type(self)),
            self.decl,
            self.code,
        )
