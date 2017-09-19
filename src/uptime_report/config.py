# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
from os.path import expanduser

from clize import converters
from configobj import ConfigObj
from sigtools import modifiers
from uptime_report.backends import backend_config, get_backend, list_backends

log = logging.getLogger(__name__)


@modifiers.autokwoargs
@modifiers.annotate(output=converters.file(keep_stdio_open=True, mode='wb'))
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


def read_config(config='~/.config/uptime_report.cfg'):
    try:
        return ConfigObj(expanduser(config))
    except IOError as e:
        log.exception("reading config file %s", config)
        print("Error reading config file: {}".format(e))
