import arrow
import attr
import enum

from attr.converters import optional
from attr.validators import in_


class OutageType(enum.Enum):
    DOWN = "down"


class ResultType(enum.Enum):
    UP = "up"
    DOWN = "down"
    UNCONFIRMED = "unconfirmed"
    UNKNOWN = "unknown"


@attr.s
class Result(object):
    """Base result class."""
    time = attr.ib(convert=arrow.get)
    check = attr.ib()
    type = attr.ib(validator=in_(ResultType))
    meta = attr.ib(default=attr.Factory(dict))


@attr.s
class Outage(object):
    """Base outage class."""
    start = attr.ib(convert=optional(arrow.get))
    finish = attr.ib(convert=optional(arrow.get))
    monitor = attr.ib()
    type = attr.ib(validator=in_(OutageType))
