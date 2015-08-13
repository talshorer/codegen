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


class Variable(Expr):

    def __init__(self, decl, value=None):
        self.decl = decl
        self.value = value
        self.expr = str(decl)

    def _act(self, source):
        Expr._act(self, source)
        if self.value is not None:
            source.write(" = ")
            self.value._act(source)


class Block(Code):

    def __init__(self, variables=None, code=None):
        if variables is None:
            variables = []
        self.vars = variables
        if code is None:
            code = []
        self.code = code

    def add_code(self, code):
        self.code.append(code)

    def add_var(self, var):
        self.vars.append(var)

    @staticmethod
    def _part_act(part, source):
        part._act(source)
        if isinstance(part, Expr):
            source.writeline(";")

    def _act(self, source):
        source.writeline("{")
        source.indent()
        for part in self.vars:
            self._part_act(part, source)
        if self.vars:
            source.linefeed()
        for part in self.code:
            self._part_act(part, source)
        source.dedent()
        source.writeline("}")

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            _cls_repr(type(self)),
            self.vars,
            self.code,
        )


class IfBlock(Block):

    MAGIC_WORD = "if"

    def __init__(self, cond, *args, **kw):
        self.cond = cond
        Block.__init__(self, *args, **kw)

    def _act(self, source):
        source.write("{} (".format(self.MAGIC_WORD))
        self.cond._act(source)
        source.write(") ")
        Block._act(self, source)

    def __repr__(self):
        return "{}({!r}, {!r}, {!r})".format(
            _cls_repr(type(self)),
            self.cond,
            self.vars,
            self.code,
        )


class WhileLoop(IfBlock):

    MAGIC_WORD = "while"


class Func(Block):

    def __init__(self, decl, *args, **kw):
        self.decl = decl
        Block.__init__(self, *args, **kw)

    def _act(self, source):
        source.writeline(str(self.decl))
        Block._act(self, source)

    def __repr__(self):
        return "{}({!r}, {!r}, {!r})".format(
            _cls_repr(type(self)),
            self.decl,
            self.vars,
            self.code,
        )
