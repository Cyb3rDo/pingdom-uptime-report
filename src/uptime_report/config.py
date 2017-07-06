from __future__ import unicode_literals

from clize.converters import file
from configobj import ConfigObj
from sigtools import modifiers
from uptime_report.backends import backend_config, get_backend, list_backends


@modifiers.kwoargs('output')
@modifiers.annotate(output=file(keep_stdio_open=True, mode='wb'))
def write_config(output='-'):
    """Write out a sample config file. Use '-' for stdout.

    :param output: the path to the file to write.
    """
    cfg = ConfigObj()
    for name in list_backends():
        cfg[name] = {}
        for setting, value in backend_config(get_backend(name)):
            cfg[name][setting] = value
    with output as fp:
        cfg.write(getattr(fp, 'buffer', fp))
