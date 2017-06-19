from __future__ import unicode_literals

from clize.converters import file
from sigtools import modifiers


@modifiers.kwoargs('output')
@modifiers.annotate(output=file(keep_stdio_open=True, mode='w'))
def write_config(output='-'):
    """Write out a sample config file. Use '-' for stdout.

    :param output: the path to the file to write.
    """
    with output as fp:
        fp.write("hi!\n")
