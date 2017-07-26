# -*- coding: utf-8 -*-
"""Formats related CLI utilities.

This module contains `clize`_. related to formats.

.. _clize:
   https://github.com/epsy/clize

"""
from enum import Enum
from operator import attrgetter

from clize import errors, parameters, parser
from sigtools import modifiers, wrappers
from uptime_report.gsheet import SheetWriter


@parser.value_converter
class Format(Enum):
    """Enumeration of existing output format types."""

    TEXT = 'txt'
    CSV = 'csv'
    JSON = 'json'
    GSHEET = 'gsheet'


DEFAULT_FORMAT = Format.TEXT
"""str: the name of the default format."""


@wrappers.decorator
@modifiers.autokwoargs
@modifiers.annotate(fmt=parameters.one_of(*map(attrgetter('value'), Format)))
def with_format(wrapped, fmt=DEFAULT_FORMAT, *args, **kwargs):
    """Provide ``--format`` argument.

    Args:
        format (str, optional): one of :class:`Format` values. Defaults to
            ``'text'``.

    Raises:
        clize.errors.CliValueError: if the format argument is invalid.
    """
    if fmt == 'gsheet' and SheetWriter is None:
        raise errors.CliValueError('pygsheets module is required.')
    return wrapped(fmt=Format(fmt), *args, **kwargs)
