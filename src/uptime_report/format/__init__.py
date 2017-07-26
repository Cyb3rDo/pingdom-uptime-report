# -*- coding: utf-8 -*-
"""Formats related CLI utilities.

This module contains `clize`_. related to formats.

.. _clize:
   https://github.com/epsy/clize

"""
import importlib
from enum import Enum
from operator import attrgetter

from clize import errors, parameters, parser
from sigtools import modifiers, wrappers


@parser.value_converter
class Format(Enum):
    """Enumeration of existing output format types."""

    TEXT = 'txt'
    CSV = 'csv'
    JSON = 'json'
    GSHEET = 'gsheet'

    @property
    def writer(self):
        mod = importlib.import_module('.' + self.value, __name__)
        return mod.Writer


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
    if fmt.writer is None:
        raise errors.CliValueError(
            '{} is unavailable (missing requirements?)'.format(fmt.value))
    return wrapped(fmt=Format(fmt), *args, **kwargs)
