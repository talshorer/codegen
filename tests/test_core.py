#! /usr/bin/python3

import io
import unittest

from codegen.core import source, code

base_config = dict(
    indentation="indent",
    seperate_elements=True,
)


class CoreTest(unittest.TestCase):

    def check_gen(self, callback, **extra_config):
        config = base_config.copy()
        config.update(extra_config)
        sourceobj = source.Source(source.SourceConfig(**config))
        expected = callback(sourceobj)
        stream = io.StringIO()
        sourceobj.make(stream)
        self.assertEqual(stream.getvalue(), expected)


class TestCode(CoreTest):

    def test_code_act(self):
        with self.assertRaises(NotImplementedError):
            code.Code()._act(None)

    def test_empty_line(self):
        def callback(sourceobj):
            sourceobj.add_element(code.empty_line)
            return "\n"
        self.check_gen(callback)


class Dummy(code.Code):

    def __init__(self, act):
        self._act = act


class TestSource(CoreTest):

    def test_config_indent(self):
        def callback(sourceobj):
            def act(sourceobj):
                sourceobj.indent()
                sourceobj.write("")
            sourceobj.add_element(Dummy(act))
            return "indent"
        self.check_gen(callback)

    _test_config_seperate_elements_dummy = (
        Dummy(lambda sourceobj: sourceobj.writeline("dummy")))

    def test_config_seperate_elements_true(self):
        def callback(sourceobj):
            sourceobj.add_element(self._test_config_seperate_elements_dummy)
            sourceobj.add_element(self._test_config_seperate_elements_dummy)
            return "dummy\n\ndummy\n"
        self.check_gen(callback, seperate_elements=True)

    def test_config_seperate_elements_false(self):
        def callback(sourceobj):
            sourceobj.add_element(self._test_config_seperate_elements_dummy)
            sourceobj.add_element(self._test_config_seperate_elements_dummy)
            return "dummy\ndummy\n"
        self.check_gen(callback, seperate_elements=False)
