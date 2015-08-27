#! /usr/bin/python3

from tests.lang.c.common import CCodeTest

from codegen.lang.c import cdata


class TestIntLiteral(CCodeTest):

    def test_decimal_int_literal(self):
        self.check_gen(cdata.IntLiteral(20), "20")

    def test_hexadecimal_int_literal(self):
        self.check_gen(cdata.IntLiteral(20, cdata.IntLiteral.B_HEX), "0x14")


class TestStringLiteral(CCodeTest):

    def test_simple_string_literal(self):
        self.check_gen(cdata.StringLiteral("hello"), "\"hello\"")

    def test_escaped_string_literal(self):
        self.check_gen(cdata.StringLiteral("hello\\\"\\n"), "\"hello\\\"\\n\"")
