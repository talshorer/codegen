#! /usr/bin/python3

from codegen.core.code import Code


def _cls_repr(cls):
    return "{}.{}".format(cls.__module__, cls.__name__)


class CCode(Code):
    pass


class Expr(CCode):

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

    def _var_act(self, source):
        Expr._act(self, source)
        if self.value is not None:
            source.write(" = ")
            self.value._act(source)


class Block(CCode):

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
    def _parts_act(source, parts, attr="_act"):
        for part in parts:
            getattr(part, attr)(source)
            if isinstance(part, Expr):
                source.writeline(";")

    def _act(self, source):
        source.writeline("{")
        source.indent()
        self._parts_act(source, self.vars, attr="_var_act")
        if self.vars:
            source.linefeed()
        self._parts_act(source, self.code)
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
