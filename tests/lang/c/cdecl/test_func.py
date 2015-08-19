#! /usr/bin/python3

import unittest

from codegen.lang.c import cdecl

ct_int = cdecl.Primitive("int")


class TestFuncWithSingleArg(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Func(ct_int, [ct_int("b")])("a")
        self.assertEqual(str(decl), "int a(int b)")


class TestFuncWithVoidArgs(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Func(ct_int, cdecl.void_args)("a")
        self.assertEqual(str(decl), "int a(void)")


class TestFuncWithMultipleArgs(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Func(ct_int, [ct_int("b"), ct_int("c")])("a")
        self.assertEqual(str(decl), "int a(int b, int c)")
