#! /usr/bin/python3

import unittest

from codegen.lang.c import cpp

from tests.lang.c.test_ccode import CCodeTest, dummy


class TestNotImplementedErrors(unittest.TestCase):

    def test_include_file_with_no_enclosers(self):
        with self.assertRaises(NotImplementedError):
            cpp._IncludeFile(None)


class TestInclude(CCodeTest):

    def test_local_include_file(self):
        self.check_gen(cpp.LocalIncludeFile("file"), "\"file\"")

    def test_global_include_file(self):
        self.check_gen(cpp.GlobalIncludeFile("file"), "<file>")

    def test_include_directive(self):
        self.check_gen(cpp.Include(dummy), "#include dummy\n")
