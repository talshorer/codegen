#! /usr/bin/python3

import unittest
import io

from codegen.core import source


class LangTest(unittest.TestCase):

    # override to get wanted language config
    CONFIG = None

    def __init__(self, *args, **kw):
        if self.CONFIG is None:
            raise NotImplementedError("This is an abstract class")
        unittest.TestCase.__init__(self, *args, **kw)

    def check_gen(self, element, expected, action="_act"):
        stream = io.StringIO()
        sourceobj = source._SourceStream(self.CONFIG, stream)
        getattr(element, action)(sourceobj)
        self.assertEqual(stream.getvalue(), expected)
