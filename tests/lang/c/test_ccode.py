#! /usr/bin/python3

import unittest
import io

from codegen.lang.c import ccode, csource
from codegen.core import source

dummy = ccode.Expr("dummy")


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
        self.check_gen(
            ccode.Expr("0 + 1"),
            "(0 + 1)",
            action="_act_with_parentheses",
        )
