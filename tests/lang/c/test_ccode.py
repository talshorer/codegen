#! /usr/bin/python3

import unittest
import io

from codegen.lang.c import ccode, cdecl, csource
from codegen.core import source, code

dummy = ccode.Expr("dummy")
dummy_parentheses = ccode.Expr("0 + 1")
ct_int = cdecl.Primitive("int")


class CCodeTest(unittest.TestCase):

    def check_gen(self, element, expected, action="_act"):
        stream = io.StringIO()
        sourceobj = source._SourceStream(csource._config, stream)
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

    def test_to_args(self):
        decls = [ct_int("a"), ct_int("b")]
        variables = [ccode.Variable(decl) for decl in decls]
        self.assertEqual(ccode.Variable.to_args(variables), decls)


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

    def test_binary_parentheses(self):
        self.check_gen(
            ccode.Addition(dummy, dummy),
            "(dummy + dummy)",
            action="_act_with_parentheses",
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
        self.check_gen(ccode.Block(code=[dummy]), "\tdummy;\n")

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
        self.check_gen(block, "\tdummy;\n")

    def test_add_var(self):
        block = ccode.Block()
        block.add_var(ccode.Variable(ct_int("a")))
        self.check_gen(block, (
            "{\n"
            "\tint a;\n"
            "\n"
            "}\n"
        ))


class TestIfBlock(CCodeTest):

    def test_if(self):
        self.check_gen(ccode.IfBlock(dummy), (
            "if (dummy) {\n"
            "}\n"
        ))

    def check_simple_if_else(self, element):
        self.check_gen(element, (
            "if (dummy) {\n"
            "} else {\n"
            "}\n"
        ))

    def test_if_else(self):
        ifb = ccode.IfBlock(dummy, elseb=ccode.ElseBlock())
        self.check_simple_if_else(ifb)

    def test_if_else_with_single_expression(self):
        elseb = ccode.ElseBlock()
        self.check_gen(ccode.IfBlock(dummy, code=[dummy], elseb=elseb), (
            "if (dummy) {\n"
            "\tdummy;\n"
            "} else {\n"
            "}\n"
        ))

    def test_if_else_if(self):
        elseb = ccode.ElseBlock(code=[ccode.IfBlock(dummy)])
        self.check_gen(ccode.IfBlock(dummy, elseb=elseb), (
            "if (dummy) {\n"
            "} else if (dummy) {\n"
            "}\n"
        ))

    def test_if_else_with_multiple_expressions_in_else(self):
        elseb = ccode.ElseBlock(code=[ccode.IfBlock(dummy), dummy])
        self.check_gen(ccode.IfBlock(dummy, elseb=elseb), (
            "if (dummy) {\n"
            "} else {\n"
            "\tif (dummy) {\n"
            "\t}\n"
            "\tdummy;\n"
            "}\n"
        ))

    def test_if_else_if_else(self):
        elseb = ccode.ElseBlock()
        elseifb = ccode.ElseBlock(code=[ccode.IfBlock(dummy, elseb=elseb)])
        self.check_gen(ccode.IfBlock(dummy, elseb=elseifb), (
            "if (dummy) {\n"
            "} else if (dummy) {\n"
            "} else {\n"
            "}\n"
        ))

    def test_add_else(self):
        ifb = ccode.IfBlock(dummy)
        ifb.add_else(ccode.ElseBlock())
        self.check_simple_if_else(ifb)

    def test_add_else_with_existing_else(self):
        ifb = ccode.IfBlock(dummy, elseb=ccode.ElseBlock())
        with self.assertRaises(code.CodeError):
            ifb.add_else(ccode.ElseBlock())
        self.check_simple_if_else(ifb)


class TestWhileLoop(CCodeTest):

    def test_while(self):
        self.check_gen(ccode.WhileLoop(dummy), (
            "while (dummy) {\n"
            "}\n"
        ))


class TestCall(CCodeTest):

    def test_call_no_params(self):
        self.check_gen(ccode.Call(dummy, []), "dummy()")

    def test_call_one_param(self):
        self.check_gen(ccode.Call(dummy, [dummy]), "dummy(dummy)")

    def test_call_multiple_params(self):
        call = ccode.Call(dummy, [dummy, dummy])
        self.check_gen(call, "dummy(dummy, dummy)")

    def test_call_unary_operation(self):
        self.check_gen(ccode.Call(ccode.Dereference(dummy), []), "(*dummy)()")


class TestFunc(CCodeTest):

    def test_simple_func(self):
        self.check_gen(ccode.Func(cdecl.Func(ct_int, cdecl.void_args)("a")), (
            "int a(void)\n"
            "{\n"
            "}\n"
        ))

    def test_to_expr(self):
        expr = ccode.Func(cdecl.Func(ct_int, cdecl.void_args)("a")).to_expr()
        self.check_gen(expr, "a")


class TestCast(CCodeTest):

    def test_cast(self):
        self.check_gen(ccode.Cast(ct_int, dummy), "(int)dummy")


class TestSubscript(CCodeTest):

    def test_subscript_simple(self):
        call = ccode.Subscript(dummy, dummy)
        self.check_gen(call, "dummy[dummy]")

    def test_subsript_unary_operation(self):
        element = ccode.Subscript(ccode.Dereference(dummy), dummy)
        self.check_gen(element, "(*dummy)[dummy]")
