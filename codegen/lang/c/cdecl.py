#! /usr/bin/python3


class CDecl(object):

    def __init__(self, ctype, name):
        self.ctype = ctype
        self.name = name

    def __str__(self):
        return self.ctype._make(self.name)


class NamelessArg(CDecl):

    def __init__(self, ctype):
        CDecl.__init__(self, ctype, "")


class _CType(object):

    def _make(self):
        raise NotImplementedError("This is an abstract class")

    def __call__(self, name):
        return CDecl(self, name)


class Primitive(_CType):

    def __init__(self, typename):
        self.typename = typename

    def _make(self, decl):
        return " ".join(s for s in (self.typename, decl) if s)


void_args = (NamelessArg(Primitive("void")),)


class _SuffixType(_CType):
    pass


class Pointer(_CType):

    def __init__(self, ptype):
        self.ptype = ptype

    def _make(self, decl):
        base_fmt = "*{}".format(format(decl))
        if isinstance(self.ptype, _SuffixType):
            base_fmt = "({})".format(base_fmt)
        return self.ptype._make(base_fmt)


class Array(_SuffixType):

    def __init__(self, etype, size=""):
        self.etype = etype
        self.size = size

    def _make(self, decl):
        return self.etype._make("{}[{}]".format(decl, self.size))


class Func(_SuffixType):

    def __init__(self, rettype, args):
        self.rettype = rettype
        self.args = args
        self._args_str = ", ".join(str(a) for a in args)

    def _make(self, decl):
        return self.rettype._make("{}({})".format(decl, self._args_str))
