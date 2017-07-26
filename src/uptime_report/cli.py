# -*- coding: utf-8 -*-
"""Uptime report CLI.

This module contains all CLI entrypoints. Command line argument parsing and
execution is implemented via `clize`_.

Examples::

    $ python -m uptime_report.cli --version

.. _clize:
   https://github.com/epsy/clize

"""
from __future__ import print_function, unicode_literals

import logging
import sys

from clize import errors, parser, run
from sigtools import modifiers, wrappers
from uptime_report._version import get_versions
from uptime_report.backends import get_backend, list_backends
from uptime_report.config import read_config, write_config
from uptime_report.format import with_format
from uptime_report.outage import Outage, get_downtime_in_seconds, get_outages
from uptime_report.time import get_time

try:
    import requests_cache
except ImportError:
    requests_cache = None


DEFAULT_BACKEND = 'pingdom'
"""str: name of default backend module."""


DEFAULT_CONFIG = '~/.config/uptime_report.cfg'
"""str: path to default config file."""


@parser.value_converter
def get_log_level(level):
    """Convert a value to a log level.

    Converts a case-insensitive log level name to the corresponding
    integer value from Python's :mod:`logging` package.

    Example:

        >>> assert logging.DEBUG == get_log_level('debug')

    Args:
        level (str): the value to convert

    Returns:
        int: a log level from the :mod:`logging` package.

    Raises:
        clize.errors.CliValueError: if the value cannot be converted.

    """
    try:
        return getattr(logging, level.upper())
    except AttributeError:
        raise errors.CliValueError(
            'Invalid log level: {}'.format(level))


@wrappers.decorator
@modifiers.autokwoargs
@modifiers.annotate(log_level=get_log_level)
def with_common_args(
        wrapped, log_level=None, use_cache=False, config=DEFAULT_CONFIG,
        *args, **kwargs):
    """Add common CLI arguments to a method.

    Provides ``--log-level``, ``--config`` and ``--use-cache`` options.

    Args:
        log_level (int): the log level code to configure logging.
        use_cache (bool): True if you want `requests_cache`_ to be used.

    .. _requests_cache:
       https://github.com/reclosedev/requests-cache
    """
    logging.basicConfig(level=log_level or logging.ERROR)
    if use_cache:
        if requests_cache:
            requests_cache.install_cache()
        else:
            print("Cache disabled, missing requests-cache module.")
    return wrapped(config=read_config(config), *args, **kwargs)


@wrappers.decorator
@modifiers.autokwoargs
def with_backend(wrapped, backend=DEFAULT_BACKEND, *args, **kwargs):
    """Provide ``--backend`` option that initializes a backend.

    Args:
        backend (str, optional): the name of the backend. Defaults to
            ``'pingdom'``.

    Raises:
        clize.errors.CliValueError: if the backend configuration is missing
    """
    try:
        cfg = kwargs.get('config', {})[backend]
    except (TypeError, KeyError):
        raise errors.CliValueError(
            "Missing configuration for backend {}".format(backend))
    impl = get_backend(backend).from_config(cfg)
    return wrapped(backend=impl, *args, **kwargs)


@wrappers.decorator
@modifiers.autokwoargs
@modifiers.annotate(start=get_time, finish=get_time)
def with_filters(
        wrapped, start, finish, overlap=0, minlen=300,
        *args, **kwargs):
    """Provide common filter arguments.

    Args:
        start (str): the start time in a string parseable by
            :py:func:`get_time`.
        finish (str): the finish time in a string parseable by
            :py:func:`get_time`.
        overlap (int, optional): how many seconds must be between two outage
            periods so they don't get merged.
        minlen (int, optional): how many seconds must an outage period be so
            that it's not filtered out.

    Raises:
        clize.errors.CliValueError: if one of the values cannot be converted.
    """

    filters = {
        'start': start,
        'finish': finish,
        'overlap': overlap,
        'minlen': minlen
    }
    return wrapped(filters=filters, *args, **kwargs)


@with_common_args
@with_filters
@with_backend
@with_format
def outages(filters=None, backend=None, fmt=None, config=None):
    """List outages.

    Args:
        filters (dict): parameters to filter outages with.
        backend (object): the backend instace object
        fmt (Format): what format to output data as.
        config (dict): the settings object
    """
    outages = get_outages(backend, **filters)
    try:
        cfg = config[fmt.value]
    except (TypeError, KeyError):
        raise errors.CliValueError(
            "Missing configuration for format {}".format(fmt.value))
    fmt.writer(sys.stdout, outages, fields=Outage.fields(), config=cfg)


@with_common_args
@with_filters
@with_backend
def uptime(filters=None, backend=None):
    """Do the uptime reporting stuff."""
    outages = get_outages(backend, **filters)
    downtime = get_downtime_in_seconds(outages)
    print(downtime)


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
