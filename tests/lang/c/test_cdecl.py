#! /usr/bin/python3

import unittest

from codegen.lang.c import cdecl

ct_int = cdecl.Primitive("int")


class TestPrimitive(unittest.TestCase):

    def test_primitive(self):
        decl = cdecl.Primitive("int")("a")
        self.assertEqual(str(decl), "int a")


class TestPointer(unittest.TestCase):

    def test_pointer_to_primitive(self):
        decl = cdecl.Pointer(ct_int)("a")
        self.assertEqual(str(decl), "int *a")

    def test_pointer_to_pointer(self):
        decl = cdecl.Pointer(cdecl.Pointer(ct_int))("a")
        self.assertEqual(str(decl), "int **a")

    def test_pointer_to_array(self):
        decl = cdecl.Pointer(cdecl.Array(ct_int, 1))("a")
        self.assertEqual(str(decl), "int (*a)[1]")

    def test_pointer_to_func(self):
        decl = cdecl.Pointer(cdecl.Func(ct_int, cdecl.void_args))("a")
        self.assertEqual(str(decl), "int (*a)(void)")


class TestFunc(unittest.TestCase):

    def test_func_with_single_arg(self):
        decl = cdecl.Func(ct_int, [ct_int("b")])("a")
        self.assertEqual(str(decl), "int a(int b)")

    def test_func_with_void_args(self):
        decl = cdecl.Func(ct_int, cdecl.void_args)("a")
        self.assertEqual(str(decl), "int a(void)")

    def test_func_with_multiple_args(self):
        decl = cdecl.Func(ct_int, [ct_int("b"), ct_int("c")])("a")
        self.assertEqual(str(decl), "int a(int b, int c)")


class TestArray(unittest.TestCase):

    def test_array_of_primitive(self):
        decl = cdecl.Array(ct_int, 1)("a")
        self.assertEqual(str(decl), "int a[1]")

    def test_array_of_pointer(self):
        decl = cdecl.Array(cdecl.Pointer(ct_int), 1)("a")
        self.assertEqual(str(decl), "int *a[1]")

    def test_array_of_array(self):
        decl = cdecl.Array(cdecl.Array(ct_int, 1), 1)("a")
        self.assertEqual(str(decl), "int a[1][1]")
