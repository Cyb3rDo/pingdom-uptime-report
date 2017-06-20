import arrow
import attr
import enum

from attr.validators import in_


class OutageType(enum.Enum):
    DOWN = "down"


@attr.s
class Outage(object):
    """Base outage class."""
    start = attr.ib(convert=arrow.get)
    finish = attr.ib(convert=arrow.get)
    check = attr.ib(default=attr.NOTHING)
    type = attr.ib(default=OutageType.DOWN, validator=in_(OutageType))
