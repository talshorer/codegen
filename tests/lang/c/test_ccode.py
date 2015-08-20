#! /usr/bin/python3

import unittest
import io

from codegen.lang.c import ccode, cdecl, csource
from codegen.core import source

dummy = ccode.Expr("dummy")
dummy_parentheses = ccode.Expr("0 + 1")
ct_int = cdecl.Primitive("int")


class CCodeTest(unittest.TestCase):

    def check_gen(self, element, expected, action="_act"):
        stream = io.StringIO()
        sourceobj = source._SourceStream(csource._config, stream, [])
        getattr(element, action)(sourceobj)
        self.assertEqual(stream.getvalue(), expected)


class TestExpr(CCodeTest):

    def test_simple_expr(self):
        self.check_gen(dummy, "dummy")

    def test_parentheses_on_simple_expr(self):
        self.check_gen(dummy, "dummy", action="_act_with_parentheses")

    def test_parentheses_on_complex_expr(self):
        expr = dummy_parentheses
        self.check_gen(expr, "(0 + 1)", action="_act_with_parentheses")


class TestVariable(CCodeTest):

    def test_variable_name(self):
        self.check_gen(ccode.Variable(ct_int("a")), "a")

    def test_variable_name_with_initial(self):
        self.check_gen(ccode.Variable(ct_int("a"), dummy), "a")

    def test_variable_definition(self):
        self.check_gen(ccode.Variable(ct_int("a")), "int a", action="_var_act")

    def test_variable_definition_with_initial(self):
        var = ccode.Variable(ct_int("a"), dummy)
        self.check_gen(var, "int a = dummy", action="_var_act")


class TestBinaryOperation(CCodeTest):

    def test_simple_binary_ops(self):
        for op in [
            ccode.Addition,
            ccode.Subtraction,
            ccode.Multiplication,
            ccode.Division,
            ccode.Modulo,
            ccode.Assignment,
            ccode.AssignmentAddition,
            ccode.AssignmentSubtraction,
            ccode.AssignmentMultiplication,
            ccode.AssignmentDivision,
            ccode.AssignmentModulo,
            ccode.Equal,
            ccode.Unequal,
            ccode.LessThan,
            ccode.LessEqualThan,
            ccode.GreaterThan,
            ccode.GreaterEqualThan,
            ccode.LeftShift,
            ccode.RightShift,
            ccode.And,
            ccode.Or,
            ccode.Xor,
            ccode.LogicalAnd,
            ccode.LogicalOr,
        ]:
            self.check_gen(op(dummy, dummy), "dummy {} dummy".format(op.OP))

    def test_binary_left_parentheses(self):
        self.check_gen(
            ccode.Addition(dummy_parentheses, dummy),
            "(0 + 1) + dummy",
        )

    def test_binary_right_parentheses(self):
        self.check_gen(
            ccode.Addition(dummy, dummy_parentheses),
            "dummy + (0 + 1)",
        )


class TestUnaryOperation(CCodeTest):

    def test_simple_prefix_unary_ops(self):
        for op in [
            ccode.BitNegation,
            ccode.LogicalNot,
            ccode.Minus,
            ccode.AddressOf,
            ccode.Dereference,
            ccode.PreIncrement,
            ccode.PreDecrement,
            ccode.Return,
        ]:
            self.check_gen(op(dummy), "{}dummy".format(op.OP))

    def test_prefix_unary_parentheses(self):
        self.check_gen(ccode.PreIncrement(dummy_parentheses), "++(0 + 1)")

    def test_simple_suffix_unary_ops(self):
        for op in [
            ccode.PostIncrement,
            ccode.PostDecrement,
        ]:
            self.check_gen(op(dummy), "dummy{}".format(op.OP))

    def test_suffix_unary_parentheses(self):
        self.check_gen(ccode.PostIncrement(dummy_parentheses), "(0 + 1)++")


class TestBlock(CCodeTest):

    def test_empty_block(self):
        self.check_gen(ccode.Block(), (
            "{\n"
            "}\n"
        ))

    def test_block_with_single_expression(self):
        self.check_gen(ccode.Block(code=[dummy]), (
            "\n"
            "\tdummy;\n"
        ))

    def test_block_with_multiple_expressions(self):
        self.check_gen(ccode.Block(code=[dummy, dummy]), (
            "{\n"
            "\tdummy;\n"
            "\tdummy;\n"
            "}\n"
        ))

    def test_block_with_single_variable_and_no_expressions(self):
        self.check_gen(ccode.Block(variables=[ccode.Variable(ct_int("a"))]), (
            "{\n"
            "\tint a;\n"
            "\n"
            "}\n"
        ))

    def test_block_with_single_variable_and_single_expression(self):
        self.check_gen(ccode.Block(
            variables=[ccode.Variable(ct_int("a"))],
            code=[dummy],
        ), (
            "{\n"
            "\tint a;\n"
            "\n"
            "\tdummy;\n"
            "}\n"
        ))

    def test_add_code(self):
        block = ccode.Block()
        block.add_code(dummy)
        self.check_gen(block, (
            "\n"
            "\tdummy;\n"
        ))

    def test_add_var(self):
        block = ccode.Block()
        block.add_var(ccode.Variable(ct_int("a")))
        self.check_gen(block, (
            "{\n"
            "\tint a;\n"
            "\n"
            "}\n"
        ))
