#! /usr/bin/python3


class Code(object):

    def _act(self, source):
        raise NotImplementedError("This is an abstract class")


class _EmptyLine(object):

    def _act(self, source):
        source.linefeed()


empty_line = _EmptyLine()
