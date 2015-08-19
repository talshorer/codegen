#! /usr/bin/python3

import unittest

from codegen.lang.c import cdecl


class TestPrimitive(unittest.TestCase):

    def runTest(self):
        decl = cdecl.Primitive("int")("a")
        self.assertEqual(str(decl), "int a")
