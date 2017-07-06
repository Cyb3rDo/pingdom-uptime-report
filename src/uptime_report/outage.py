import enum
from itertools import chain

import arrow
import attr
from attr.converters import optional
from attr.validators import in_


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


def merge_outages(outages, overlap=0):
    """Merge a list of Outage objects."""
    beginning_of_time = arrow.get(0).replace(microsecond=0)
    end_of_time = arrow.utcnow().replace(years=2**10, microsecond=0)

    def sortkey(value):
        """Handle None values as very far in the past or future."""
        if value[0]:
            return value[0]  # value as-is
        if value[1] > 0:     # open beginning
            return beginning_of_time.timestamp
        return end_of_time.timestamp  # open ending

    def make_ranges(changes):
        """Combine changes to create new ranges."""
        start = None               # placeholder
        n = 0                      # the number of range openings
        for t, state in changes:
            if t and state < 0:    # range close, correct overlap
                t -= overlap
            if n == 0:             # new range starting
                start = t
            n += state             # count open ranges
            if n == 0:             # all ranges closed
                yield start, t

    def change(outage):
        start = outage.start.timestamp if outage.start else None
        finish = outage.finish.timestamp + overlap if outage.finish else None
        return ((start, 1), (finish, -1))

    # flatten the outages into a list of open or close changes
    flat = chain.from_iterable(change(o) for o in outages)

    # sort the changes based on time
    outage_changes = sorted(flat, key=sortkey)

    # make new outage objects from new ranges
    for start, finish in make_ranges(outage_changes):
        yield Outage(start=start, finish=finish)
