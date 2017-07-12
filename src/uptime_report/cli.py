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

import json
import logging
import sys
from enum import Enum
from operator import attrgetter

import arrow
from clize import errors, parameters, parser, run
from sigtools import modifiers, wrappers
from uptime_report._version import get_versions
from uptime_report.backends import get_backend, list_backends
from uptime_report.config import read_config, write_config
from uptime_report.outage import (encode_outage, get_downtime_in_seconds,
                                  get_outages, print_outages,
                                  write_outages_csv)

try:
    import requests_cache
except ImportError:
    requests_cache = None


DEFAULT_BACKEND = 'pingdom'
"""str: name of default backend module."""


@parser.value_converter
class Format(Enum):
    """Enumeration of existing output format types."""

    TEXT = 'txt'
    CSV = 'csv'
    JSON = 'json'


DEFAULT_FORMAT = Format.TEXT


class TimeUnits(Enum):
    """Enumeration of time division abbreviations.

    Attributes:
        minutes (str): ``m``
        hours (str): ``h``
        days (str): ``d``
        months (str): ``mo``
        years (str): ``y``
    """

    minutes = 'm'
    hours = 'h'
    days = 'd'
    months = 'mo'
    years = 'y'


@parser.value_converter
def get_time(value, now=None):
    """Convert a parameter to a timestamp.

    Based on the passed value create a timestamp that represents the
    value. Both absolute and relative forms are supported::

    Example:

        >>> get_time('2017-06-03')
        1496448000
        >>> now = arrow.utcnow().replace(microsecond=0).timestamp
        >>> get_time('+2d') == now + 2*60*60*24
        True

    Valid time units for relative values are described in :class:`TimeUnits`.
    If a time unit is not provided the default is :py:attr:`TimeUnits.days`.

    Additionally, for relative values, the current time can be specified by
    passing an :class:`~arrow.arrow.Arrow` instance as the ``now``
    argument::

    Example:

        >>> today = get_time('2017-06-03')
        >>> get_time('+1d', arrow.get(today))
        1496534400

    Args:
        value (str): the value to convert
        now (:obj:`~arrow.arrow.Arrow`, optional): the base time to use
            for relative values.

    Returns:
        int: a timestamp

    Raises:
        clize.errors.CliValueError: if the value cannot be converted.

    """

    now = arrow.utcnow() if not now else now.replace(microsecond=0)
    if not value:
        return now.timestamp
    if value.startswith('-') or value.startswith('+'):
        op = value[0]
        val = value[1:]
        try:
            num = ''.join([c for c in val if c.isdigit()])
            if len(num) < len(val):
                unit = TimeUnits(val[len(num):])
            else:
                unit = TimeUnits('d')
            d = now.replace(**{unit.name: int(op + num)})
            return d.timestamp
        except ValueError:
            pass
    try:
        return arrow.get(value).timestamp
    except arrow.parser.ParserError as e:
        raise errors.CliValueError(e)


@parser.value_converter
def get_log_level(level):
    """Convert a value to a log level.

    Converts a case-insensitive log level name to the corresponding
    integer value from Python's :mod:`logging` package::

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
        wrapped, log_level=None, use_cache=False, *args, **kwargs):
    logging.basicConfig(level=log_level or logging.ERROR)
    if use_cache:
        if requests_cache:
            requests_cache.install_cache()
        else:
            print("Cache disabled, missing requests-cache module.")
    return wrapped(*args, **kwargs)


@wrappers.decorator
@modifiers.autokwoargs
def with_backend(wrapped, backend=DEFAULT_BACKEND, *args, **kwargs):
    try:
        config = read_config()[backend]
    except KeyError:
        raise errors.CliValueError(
            "Missing configuration for backend {}".format(backend))
    impl = get_backend(backend).from_config(config)
    return wrapped(backend=impl, *args, **kwargs)


@wrappers.decorator
@modifiers.autokwoargs
@modifiers.annotate(start=get_time, finish=get_time)
def with_filters(
        wrapped, start, finish, overlap=0, minlen=300,
        *args, **kwargs):
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
@modifiers.annotate(fmt=parameters.one_of(*map(attrgetter('value'), Format)))
def outages(filters=None, backend=None, fmt=DEFAULT_FORMAT):
    """List outages."""
    outages = get_outages(backend, **filters)

    if fmt == Format.JSON:
        print(json.dumps(list(outages), indent=4, default=encode_outage))
    elif fmt == Format.CSV:
        write_outages_csv(sys.stdout, outages)
    else:
        print_outages(outages)


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
