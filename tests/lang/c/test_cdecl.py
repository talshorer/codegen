#! /usr/bin/python3

import unittest

from tests.lang.c.common import ct_int

from codegen.lang.c import cdecl


class TestNotImplementedErrors(unittest.TestCase):

    def test_ctype_make(self):
        with self.assertRaises(NotImplementedError):
            cdecl._CType()._make()


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

    def test_func_with_nameless_args(self):
        nameless_arg = cdecl.NamelessArg(ct_int)
        decl = cdecl.Func(ct_int, [nameless_arg, nameless_arg])("a")
        self.assertEqual(str(decl), "int a(int, int)")


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

    def test_unknown_size_array(self):
        decl = cdecl.Array(ct_int)("a")
        self.assertEqual(str(decl), "int a[]")


class TestNamelessArg(unittest.TestCase):

    def test_nameless_pointer(self):
        decl = cdecl.NamelessArg(cdecl.Array(ct_int, 1))
        self.assertEqual(str(decl), "int [1]")

    def test_nameless_array(self):
        decl = cdecl.NamelessArg(cdecl.Array(cdecl.Pointer(ct_int), 1))
        self.assertEqual(str(decl), "int *[1]")

    def test_nameless_pointer_to_func(self):
        decl = cdecl.NamelessArg(cdecl.Pointer(cdecl.Func(
            ct_int,
            cdecl.void_args),
        ))
        self.assertEqual(str(decl), "int (*)(void)")

    def test_nameless_pointer_to_array(self):
        decl = cdecl.NamelessArg(cdecl.Pointer(cdecl.Array(ct_int, 1)))
        self.assertEqual(str(decl), "int (*)[1]")
