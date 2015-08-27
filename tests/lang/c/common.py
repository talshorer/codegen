#! /usr/bin/python3


from tests.lang import common

from codegen.lang.c import ccode, cdecl, csource

dummy = ccode.Expr("dummy")
dummy_parentheses = ccode.Expr("0 + 1")
ct_int = cdecl.Primitive("int")


class CCodeTest(common.LangTest):
    CONFIG = csource._config
