#! /usr/bin/python3

import string

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

    _IDENTIFIER_CHARS = string.digits + string.ascii_letters + "_"

    # set to a boolean value if the same behaviour is always wanted
    PARENTHESES_BEHAVIOUR = None

    def needs_parentheses(self):
        if self.PARENTHESES_BEHAVIOUR is not None:
            return self.PARENTHESES_BEHAVIOUR
        return not all(c in self._IDENTIFIER_CHARS for c in self.expr)

    @classmethod
    def exprs_from_text(cls, text):
        return [cls(part.strip()) for part in text.split(";") if part]


class Variable(Expr):

    PARENTHESES_BEHAVIOUR = False

    def __init__(self, decl, value=None):
        self.decl = decl
        self.value = value
        self.expr = decl.name  # for Expr._act

    def _var_act(self, source):
        source.write(str(self.decl))
        if self.value is not None:
            source.write(" = ")
            self.value._act(source)


class _BinaryOperation(Expr):

    OP = None
    PARENTHESES_BEHAVIOUR = True

    def __init__(self, left, right):
        if self.OP is None:
            raise NotImplementedError("This is an abstract class")
        self.left = left
        self.right = right

    def _act(self, source):
        left_needs_parentheses = self.left.needs_parentheses()
        right_needs_parentheses = self.right.needs_parentheses()
        if left_needs_parentheses:
            source.write("(")
        self.left._act(source)
        if left_needs_parentheses:
            source.write(")")
        source.write(" {} ".format(self.OP))
        if right_needs_parentheses:
            source.write("(")
        self.right._act(source)
        if right_needs_parentheses:
            source.write(")")


def _create_binary_operation(name, op):
    return type(name, (_BinaryOperation,), dict(OP=op))


Addition = _create_binary_operation("Addition", "+")
Subtraction = _create_binary_operation("Subtraction", "-")
Multiplication = _create_binary_operation("Multiplication", "*")
Division = _create_binary_operation("Division", "/")
Modulo = _create_binary_operation("Modulo", "%")
Assignment = _create_binary_operation("Assignment", "=")
AssignmentAddition = _create_binary_operation("AssignmentAddition", "+=")
AssignmentSubtraction = _create_binary_operation("AssignmentSubtraction", "-=")
AssignmentMultiplication = _create_binary_operation(
    "AssignmentMultiplication",
    "*",
)
AssignmentDivision = _create_binary_operation("AssignmentDivision", "/=")
AssignmentModulo = _create_binary_operation("AssignmentModulo", "%=")
Equal = _create_binary_operation("Equal", "==")
Unequal = _create_binary_operation("Unequal", "!=")
LessThan = _create_binary_operation("LessThan", "<")
LessEqualThan = _create_binary_operation("LessEqualThan", "<=")
GreaterThan = _create_binary_operation("GreaterThan", ">")
GreaterEqualThan = _create_binary_operation("GreaterEqualThan", ">=")
LeftShift = _create_binary_operation("LeftShift", "<<")
RightShift = _create_binary_operation("RightShift", ">>")
And = _create_binary_operation("And", "&")
Or = _create_binary_operation("Or", "|")
Xor = _create_binary_operation("Xor", "^")


class _UnaryOperation(Expr):

    OP = None
    IS_SUFFIX = False
    PARENTHESES_BEHAVIOUR = False

    def __init__(self, operand):
        if self.OP is None:
            raise NotImplementedError("This is an abstract class")
        self.operand = operand

    def _act(self, source):
        if not self.IS_SUFFIX:
            source.write(self.OP)
        operand_needs_parentheses = self.operand.needs_parentheses()
        if operand_needs_parentheses:
            source.write("(")
        self.operand._act(source)
        if operand_needs_parentheses:
            source.write(")")
        if self.IS_SUFFIX:
            source.write(self.OP)


def _create_unary_operation(name, op, is_suffix=False):
    return type(name, (_UnaryOperation,), dict(OP=op, IS_SUFFIX=is_suffix))


BitNegation = _create_unary_operation("BitNegation", "~")
LogicalNot = _create_unary_operation("LogicalNot", "!")
Minus = _create_unary_operation("Minus", "-")
AddressOf = _create_unary_operation("AddressOf", "&")
Dereference = _create_unary_operation("Dereference", "*")
PreIncrement = _create_unary_operation("PreIncrement", "++")
PreDecrement = _create_unary_operation("PreDecrement", "--")
PostIncrement = _create_unary_operation("PostIncrement", "++", True)
PostDecrement = _create_unary_operation("PostDecrement", "--", True)


class Block(CCode):

    # set to a boolean value if the same behaviour is always wanted
    BRACELETS_BEHAVIOUR = None

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

    def needs_bracelets(self):
        if self.BRACELETS_BEHAVIOUR is not None:
            return self.BRACELETS_BEHAVIOUR
        return len(self.vars) != 0 or len(self.code) != 1

    def _act(self, source):
        needs_bracelets = self.needs_bracelets()
        if needs_bracelets:
            # not a new line, add a space before the bracelet
            if source._indented:
                source.write(" ")
            source.writeline("{")
        else:
            # start the block on a new line
            source.linefeed()
        source.indent()
        self._parts_act(source, self.vars, attr="_var_act")
        if self.vars:
            source.linefeed()
        self._parts_act(source, self.code)
        source.dedent()
        if needs_bracelets:
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
        source.write(")")
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


class FuncCall(Expr):

    PARENTHESES_BEHAVIOUR = False

    def __init__(self, funcname, args):
        self.funcname = funcname
        self.args = args

    def _act(self, source):
        source.write("{}(".format(self.funcname))
        first = True
        for arg in self.args:
            if not first:
                source.write(", ")
            first = False
            arg._act(source)
        source.write(")")


class Func(Block):

    BRACELETS_BEHAVIOUR = True

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

    def make_func_call(self, args):
        return FuncCall(self.decl.name, args)
