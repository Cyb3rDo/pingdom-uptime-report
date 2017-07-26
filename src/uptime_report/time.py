# -*- coding: utf-8 -*-
from enum import Enum

import arrow
from clize import errors, parser


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
    value. Both absolute and relative forms are supported.

    Example:

        >>> get_time('2017-06-03')
        1496448000
        >>> now = arrow.utcnow().replace(microsecond=0).timestamp
        >>> get_time('+2d') == now + 2*60*60*24
        True

    Valid time units for relative values are described in :class:`TimeUnits`.
    If a time unit is not provided the default is :py:attr:`TimeUnits.days`.

    Additionally, for relative values, the current time can be specified by
    passing an :class:`~arrow.arrow.Arrow` instance as the ``now`` argument.

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
