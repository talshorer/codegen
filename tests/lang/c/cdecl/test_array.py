#! /usr/bin/python3

import unittest

from codegen.lang.c import cdecl

ct_int = cdecl.Primitive("int")


class TestArrayOfPrimitive(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Array(ct_int, 1)("a")
        self.assertEqual(str(decl), "int a[1]")


class TestArrayOfPointer(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Array(cdecl.Pointer(ct_int), 1)("a")
        self.assertEqual(str(decl), "int *a[1]")


class TestArrayOfArray(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Array(cdecl.Array(ct_int, 1), 1)("a")
        self.assertEqual(str(decl), "int a[1][1]")
