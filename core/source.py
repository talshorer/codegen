#! /usr/bin/python3

import collections

SourceConfig = collections.namedtuple("SourceFileConfig", [
    "indentation",
    "seperate_elements",
])


class _SourceStream(object):

    def __init__(self, config, stream, elements):
        self.config = config
        self.stream = stream
        self.elements = elements
        self._indent_level = 0
        self._indented = False

    def indent(self):
        self._indent_level += 1

    def dedent(self):
        self._indent_level -= 1

    def write(self, text):
        if not self._indented:
            self.stream.write(self._indent_level *
                                     self.config.indentation)
            self._indented = True
        self.stream.write(text)

    def linefeed(self):
        self.stream.write("\n")
        self._indented = False

    def writeline(self, text):
        self.write(text)
        self.linefeed()

    def __call__(self):
        for element in self.elements:
            element._act(self)
            if self.config.seperate_elements:
                self.linefeed()


class Source(object):

    def __init__(self, config):
        self.config = config
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def make(self, stream):
        return _SourceStream(self.config, stream, self.elements)()
