#! /usr/bin/python3

from codegen.core import code


class _CppDirective(code.Code):
    pass


class _IncludeFile(_CppDirective):

    OPENER = None
    CLOSER = None

    def __init__(self, name):
        if self.OPENER == None or self.CLOSER == None:
            raise NotImplementedError("This is an abstract class")
        self.name = name

    def _act(self, source):
        source.write("{}{}{}".format(self.OPENER, self.name, self.CLOSER))

class LocalIncludeFile(_IncludeFile):

    OPENER = CLOSER = "\""

class GlobalIncludeFile(_IncludeFile):

    OPENER = "<"
    CLOSER = ">"

class Include(_CppDirective):

    def __init__(self, name):
        self.name = name

    def _act(self, source):
        source.write("#include ")
        self.name._act(source)
        source.linefeed()
