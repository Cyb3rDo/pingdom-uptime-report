# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import json
import logging
from enum import Enum

import arrow
from clize import errors, parser, run
from sigtools import modifiers, wrappers
from uptime_report._version import get_versions
from uptime_report.backends import get_backend, list_backends
from uptime_report.config import read_config, write_config
from uptime_report.outage import encode_outage, get_outages, print_outages

try:
    import requests_cache
except ImportError:
    requests_cache = None


DEFAULT_BACKEND = 'pingdom'


class TimeUnits(Enum):
    minutes = 'm'
    hours = 'h'
    days = 'd'
    months = 'm'
    years = 'y'


@parser.value_converter
def get_time(value, now=None):
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
    try:
        return getattr(logging, level.upper())
    except AttributeError:
        raise errors.CliValueError(
            'Invalid log level: {}'.format(level))


@wrappers.decorator
@modifiers.kwoargs('log_level', 'use_cache')
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
@modifiers.kwoargs('backend')
def with_backend(wrapped, backend=DEFAULT_BACKEND, *args, **kwargs):
    try:
        config = read_config()[backend]
    except KeyError:
        raise errors.CliValueError(
            "Missing configuration for backend {}".format(backend))
    impl = get_backend(backend).from_config(config)
    return wrapped(backend=impl, *args, **kwargs)


@wrappers.decorator
@modifiers.kwoargs('overlap', 'minlen')
@modifiers.annotate(start=get_time, finish=get_time)
def with_filters(
        wrapped, start=None, finish=None, overlap=0, minlen=300,
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
@modifiers.kwoargs('to_json')
def outages(filters=None, backend=None, to_json=False):
    """List outages."""
    outages = get_outages(backend, **filters)

    if to_json:
        print(json.dumps(list(outages), indent=4, default=encode_outage))
    else:
        print_outages(outages)


@with_common_args
@with_filters
@with_backend
def uptime(filters=None, backend=None):
    """Do the uptime reporting stuff."""
    pass


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
