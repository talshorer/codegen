#! /usr/bin/python3


class Code(object):

    def _act(self, source):
        raise NotImplementedError("This is an abstract class")

    @staticmethod
    def _parts_act_with_seperator(source, parts, sep):
        first = True
        for part in parts:
            if not first:
                source.write(sep)
            first = False
            part._act(source)


class _EmptyLine(Code):

    def _act(self, source):
        source.linefeed()


empty_line = _EmptyLine()


class CodeError(Exception):
    pass
