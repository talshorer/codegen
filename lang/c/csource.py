#! /usr/bin/python3

from codegen.core import source

_config = source.SourceConfig(
    indentation="\t",
    seperate_elements=True,
)


class CSource(source.Source):

    def __init__(self):
        source.Source.__init__(self, _config)
