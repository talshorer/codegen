#! /usr/bin/python3

import unittest

from codegen.lang.c import cdecl

ct_int = cdecl.Primitive("int")


class TestPointerToPrimitive(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Pointer(ct_int)("a")
        self.assertEqual(str(decl), "int *a")


class TestPointerToPointer(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Pointer(cdecl.Pointer(ct_int))("a")
        self.assertEqual(str(decl), "int **a")


class TestPointerToArray(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Pointer(cdecl.Array(ct_int, 1))("a")
        self.assertEqual(str(decl), "int (*a)[1]")


class TestPointerToFunc(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Pointer(cdecl.Func(ct_int, cdecl.void_args))("a")
        self.assertEqual(str(decl), "int (*a)(void)")
