#! /usr/bin/python3

import unittest
import io

from codegen.lang.c import ccode, cdecl, csource
from codegen.core import source

dummy = ccode.Expr("dummy")
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
        expr = ccode.Expr("0 + 1")
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
