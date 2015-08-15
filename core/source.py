#! /usr/bin/python3

import collections

SourceConfig = collections.namedtuple("SourceFileConfig", [
    "stream",
    "indentation",
    "seperate_elements",
])


class Source(object):

    def __init__(self, config):
        self.config = config
        self._indent_level = 0
        self._indented = False
        self._elements = []

    def indent(self):
        self._indent_level += 1

    def dedent(self):
        self._indent_level -= 1

    def write(self, text):
        if not self._indented:
            self.config.stream.write(self._indent_level *
                                     self.config.indentation)
            self._indented = True
        self.config.stream.write(text)

    def linefeed(self):
        self.config.stream.write("\n")
        self._indented = False

    def writeline(self, text):
        self.write(text)
        self.linefeed()

    def add_element(self, element):
        self._elements.append(element)

    def make(self):
        for element in self._elements:
            element._act(self)
            if self.config.seperate_elements:
                self.linefeed()
