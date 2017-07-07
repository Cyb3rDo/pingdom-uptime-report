from __future__ import print_function, unicode_literals

import logging

import arrow
from clize import errors, parser, run
from sigtools import modifiers, wrappers
from uptime_report._version import get_versions
from uptime_report.backends import get_backend, list_backends
from uptime_report.config import read_config, write_config

try:
    import requests_cache
except ImportError:
    requests_cache = None


def uptime():
    """Do the uptime reporting stuff."""
    pass


to_arrow = parser.value_converter(arrow.get)


@parser.value_converter
def get_log_level(level):
    try:
        return getattr(logging, level.upper())
    except AttributeError:
        raise errors.CliValueError(
            'Invalid log level: {}'.format(level))


@wrappers.decorator
@modifiers.annotate(log_level=get_log_level)
@modifiers.kwoargs('log_level', 'use_cache')
def with_common_args(
        wrapped, log_level='error', use_cache=False, *args, **kwargs):
    logging.basicConfig(level=log_level)
    if use_cache:
        if requests_cache:
            requests_cache.install_cache()
        else:
            print("Cache disabled, missing requests-cache module.")
    return wrapped(*args, **kwargs)


@with_common_args
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
    run([uptime, outages, write_config], alt=[version, backends], **kwargs)


if __name__ == '__main__':
    main()
