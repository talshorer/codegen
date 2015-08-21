#! /usr/bin/python3

import string

from codegen.core import code

from . import cdecl


class _CCode(code.Code):

    # set to a boolean value or override get_parentheses_behaviour
    PARENTHESES_BEHAVIOUR = None
    SEMICOLON_BEHAVIOUR = True

    def needs_parentheses(self):
        if self.PARENTHESES_BEHAVIOUR is None:
            return self.get_parentheses_behaviour()
        return self.PARENTHESES_BEHAVIOUR

    def get_parentheses_behaviour(self):
        raise NotImplementedError("This is an abstract class")

    def _act_with_parentheses(self, source, force=False):
        needs_parentheses = True if force else self.needs_parentheses()
        if needs_parentheses:
            source.write("(")
        self._act(source)
        if needs_parentheses:
            source.write(")")

    def _act_force_parentheses_on_unary(self, source):
        self._act_with_parentheses(source, isinstance(self, _UnaryOperation))


class Expr(_CCode):

    def __init__(self, expr):
        self.expr = expr

    def _act(self, source):
        source.write(self.expr)

    _IDENTIFIER_CHARS = string.digits + string.ascii_letters + "_"

    def get_parentheses_behaviour(self):
        return not all(c in self._IDENTIFIER_CHARS for c in self.expr)


class Variable(Expr):

    PARENTHESES_BEHAVIOUR = False

    def __init__(self, decl, value=None):
        self.decl = decl
        self.value = value
        Expr.__init__(self, decl.name)

    def _var_act(self, source):
        source.write(str(self.decl))
        if self.value is not None:
            source.write(" = ")
            self.value._act(source)

    @staticmethod
    def to_args(variables):
        return [var.decl for var in variables]


class _BinaryOperation(_CCode):

    OP = None
    PARENTHESES_BEHAVIOUR = True

    def __init__(self, left, right):
        if self.OP is None:
            raise NotImplementedError("This is an abstract class")
        self.left = left
        self.right = right

    def _act(self, source):
        self.left._act_with_parentheses(source)
        source.write(" {} ".format(self.OP))
        self.right._act_with_parentheses(source)


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
LogicalAnd = _create_binary_operation("LogicalAnd", "&&")
LogicalOr = _create_binary_operation("LogicalOr", "||")


class _UnaryOperation(_CCode):

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
        self.operand._act_with_parentheses(source)
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
Return = _create_unary_operation("Return", "return ")


class Block(_CCode):

    # set to a boolean value if the same behaviour is always wanted
    BRACELETS_BEHAVIOUR = None
    SEMICOLON_BEHAVIOUR = False
    # only valid if self.needs_bracelets()
    END_WITH_LINEFEED = True
    # only valid if not self.needs_bracelets() and source._indented
    MUST_START_ON_NEWLINE = True

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
            if part.SEMICOLON_BEHAVIOUR:
                source.writeline(";")

    def needs_bracelets(self):
        if self.BRACELETS_BEHAVIOUR is not None:
            return self.BRACELETS_BEHAVIOUR
        return len(self.vars) != 0 or len(self.code) != 1

    def _act(self, source, force_bracelets=False):
        needs_bracelets = force_bracelets or self.needs_bracelets()
        do_indent = True
        if needs_bracelets:
            # not a new line, add a space before the bracelet
            if source._indented:
                source.write(" ")
            source.writeline("{")
        elif source._indented:
            if self.MUST_START_ON_NEWLINE:
                msg = "A block that must start on a new line doesn't"
                raise code.CodeError(msg)
            else:  # seperate code from last element
                source.write(" ")
                do_indent = False
        if do_indent:
            source.indent()
        self._parts_act(source, self.vars, attr="_var_act")
        if self.vars:
            source.linefeed()
        self._parts_act(source, self.code)
        if do_indent:
            source.dedent()
        if needs_bracelets:
            source.write("}")
            if self.END_WITH_LINEFEED:
                source.linefeed()


class _CondBlock(Block):

    # Override this in child class
    MAGIC_WORD = None

    def __init__(self, cond, *args, **kw):
        if self.MAGIC_WORD is None:
            raise NotImplementedError("This is an abstract class")
        self.cond = cond
        Block.__init__(self, *args, **kw)

    def _act(self, source, *args, **kw):
        source.write("{} (".format(self.MAGIC_WORD))
        self.cond._act(source)
        source.write(")")
        Block._act(self, source, *args, **kw)


class ElseBlock(Block):

    MUST_START_ON_NEWLINE = False

    def needs_bracelets(self):
        return Block.needs_bracelets(self) or type(self.code[0]) is not IfBlock

    def _act(self, source):
        source.write(" else")  # another space will be added by Block._act()
        Block._act(self, source)


class IfBlock(_CondBlock):

    MAGIC_WORD = "if"

    def __init__(self, *args, **kw):
        elseb = kw.pop("elseb", None)
        _CondBlock.__init__(self, *args, **kw)
        self.elseb = None
        if elseb is not None:
            self.add_else(elseb)

    def add_else(self, elseb):
        if self.elseb is not None:
            msg = "Cannot attach multiple else blocks to a single if block"
            raise code.CodeError(msg)
        self.BRACELETS_BEHAVIOUR = True
        self.END_WITH_LINEFEED = False
        self.elseb = elseb

    def _act(self, source):
        # if source line is already indented, we are part of an else-if
        force_bracelets = source._indented
        _CondBlock._act(self, source, force_bracelets)
        if self.elseb:
            self.elseb._act(source)


class WhileLoop(_CondBlock):

    MAGIC_WORD = "while"


class Call(_CCode):

    PARENTHESES_BEHAVIOUR = False

    def __init__(self, func, args):
        self.func = func
        self.args = args

    def _act(self, source):
        # unary operations always need parentheses when called
        self.func._act_force_parentheses_on_unary(source)
        source.write("(")
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

    def to_expr(self):
        return Expr(self.decl.name)


class Cast(_UnaryOperation):

    PARENTHESES_BEHAVIOUR = True

    def __init__(self, casttype, value):
        self.OP = "({})".format(cdecl.NamelessArg(casttype))
        _UnaryOperation.__init__(self, value)


class Subscript(_CCode):

    PARENTHESES_BEHAVIOUR = False

    def __init__(self, arr, index):
        self.arr = arr
        self.index = index

    def _act(self, source):
        # unary operations always need parentheses when subscripted
        self.arr._act_force_parentheses_on_unary(source)
        source.write("[")
        self.index._act(source)
        source.write("]")
