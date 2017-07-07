from __future__ import print_function, unicode_literals

import logging

import arrow
from clize import parser, run
from sigtools import modifiers
from uptime_report._version import get_versions
from uptime_report.backends import get_backend, list_backends
from uptime_report.config import read_config, write_config


def uptime():
    """Do the uptime reporting stuff."""
    pass


to_arrow = parser.value_converter(arrow.get)


@modifiers.annotate(start=to_arrow, finish=to_arrow)
def outages(start, finish, backend='pingdom'):
    """List outages."""
    try:
        config = read_config()[backend]
    except KeyError:
        print("Missing configuration for backend {}".format(backend))
    else:
        impl = get_backend(backend).from_config(config)
        print("\n".join(repr(o)
                        for o in impl.get_outages(
            start=start.timestamp, finish=finish.timestamp)))


def version():
    """Get the version of this program."""
    return get_versions().get('version', 'unknown')


def backends():
    """Print supported backends."""
    return "\n".join(list_backends())


def main(**kwargs):
    """Run the CLI application."""
    logging.basicConfig(level=logging.DEBUG)
    run([uptime, outages, write_config], alt=[version, backends], **kwargs)


if __name__ == '__main__':
    main()
