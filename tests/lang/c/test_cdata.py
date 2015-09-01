#! /usr/bin/python3

from tests.lang.c.common import CCodeTest, dummy

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
        self.check_gen(cdata.StringLiteral("hello\"\n"), "\"hello\\\"\\n\"")

    def test_binray_string_literal(self):
        self.check_gen(cdata.StringLiteral("\x00\x01"), "\"\\x00\\x01\"")


class TestCompoundLiteral(CCodeTest):

    def test_empty_compound_literal(self):
        self.check_gen(cdata.CompoundLiteral([]), "{ }")

    def test_compound_literal_with_single_value(self):
        self.check_gen(cdata.CompoundLiteral([dummy]), "{ dummy }")

    def test_compound_literal_with_multiple_values(self):
        compound = cdata.CompoundLiteral([dummy, dummy])
        self.check_gen(compound, "{ dummy, dummy }")
