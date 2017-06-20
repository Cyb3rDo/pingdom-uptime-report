from __future__ import unicode_literals

from clize.converters import file
from configobj import ConfigObj
from sigtools import modifiers

from uptime_report.backends import (
    backend_config, list_backends, get_backend
)


@modifiers.kwoargs('output')
@modifiers.annotate(output=file(keep_stdio_open=True, mode='w'))
def write_config(output='-'):
    """Write out a sample config file. Use '-' for stdout.

    :param output: the path to the file to write.
    """
    cfg = ConfigObj()
    for name in list_backends():
        cfg[name] = dict(backend_config(get_backend(name)))
    with output as fp:
        cfg.write(fp)
