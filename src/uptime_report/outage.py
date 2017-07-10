from itertools import chain

import arrow
import attr
from attr.converters import optional


@attr.s
class Outage(object):
    """Base outage class."""

    start = attr.ib(convert=optional(arrow.get))
    finish = attr.ib(convert=optional(arrow.get))
    before = attr.ib(convert=optional(arrow.get), default=None)
    after = attr.ib(convert=optional(arrow.get), default=None)
    meta = attr.ib(default=attr.Factory(dict))


def encode_outage(obj):
    if isinstance(obj, Outage):
        return attr.asdict(obj)
    if isinstance(obj, arrow.Arrow):
        return obj.for_json()
    raise TypeError(repr(obj) + " is not JSON serializable")


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
        for t, state, outage in changes:
            if t and state < 0:    # range close, correct overlap
                t -= overlap
            if n == 0:             # new range starting
                start = t
                outages = []
            n += state             # count open ranges
            if outage:
                outages.append(outage)
            if n == 0:             # all ranges closed
                yield start, t, outages

    def change(outage):
        start = outage.start.timestamp if outage.start else None
        finish = outage.finish.timestamp + overlap if outage.finish else None
        return ((start, 1, outage), (finish, -1, None))

    # flatten the outages into a list of open or close changes
    flat = chain.from_iterable(change(o) for o in outages)

    # sort the changes based on time
    outage_changes = sorted(flat, key=sortkey)

    # make new outage objects from new ranges
    for start, finish, data in make_ranges(outage_changes):
        # combine groups
        groups = set([group
                      for outage in data
                      for group in outage.meta.get('groups', [])])
        meta = {}
        if groups:
            meta = {'groups': groups}
        yield Outage(start=start, finish=finish, meta=meta)


def print_outages(outages):
    for i, outage in enumerate(outages):
        print("Outage #{}\nBegin: {}\tEnd: {}\n{}\n".format(
            i, outage.start.format(), outage.finish.format(),
            outage.start.humanize(
                other=outage.finish, only_distance=True)))


def filter_outage_len(outages, minlen=0):
    for o in outages:
        if (o.finish - o.start).seconds >= minlen:
            yield o


def get_outages(backend, overlap=0, minlen=0, **kwargs):
    all_outages = backend.get_outages(**kwargs)
    outages = filter_outage_len(all_outages, minlen=minlen)
    return merge_outages(outages, overlap=overlap)
