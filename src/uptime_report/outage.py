# -*- coding: utf-8 -*-
"""Uptime report outages.

This module contains generic code for processing outages.
"""
import logging
from itertools import chain
from operator import attrgetter

import arrow
import attr
from attr.converters import optional

log = logging.getLogger(__name__)
"""Outage module logger."""


@attr.s
class Outage(object):
    """An outage.

    Attributes:
        start (:class:`~arrow.arrow.Arrow`): the start time of the
            outage period.
        finish (:class:`~arrow.arrow.Arrow`): the ending time of the
            outage period.
        before (:class:`~arrow.arrow.Arrow`, optional): last time check was ok,
            if available.
        after (:class:`~arrow.arrow.Arrow`, optional): next time check was ok,
            if available.
        meta: (dict, optinal): arbitrary metadata about this outage.

    """

    start = attr.ib(convert=optional(arrow.get))
    finish = attr.ib(convert=optional(arrow.get))
    before = attr.ib(convert=optional(arrow.get), default=None)
    after = attr.ib(convert=optional(arrow.get), default=None)
    meta = attr.ib(default=attr.Factory(dict))

    def for_json(self):
        """Return a representation of this object as a dict.

        Example:

            >>> t = arrow.utcnow()
            >>> Outage(t, t).for_json() == {
            ...    "start": t,
            ...    "finish": t,
            ...    "before": None,
            ...    "after": None,
            ...    "meta": {}
            ... }
            True

        Returns:
            list: a list of names as (:class:`str`) instances.
        """
        return attr.asdict(self)

    @property
    def humanized_duration(self):
        return self.start.humanize(other=self.finish, only_distance=True)

    def humanize(self):
        return {
            'Begin': self.start.format(),
            'End': self.finish.format(),
            'Duration': self.humanized_duration,
        }

    @classmethod
    def fields(cls):
        """Return the field names for this class.

        Example:

            >>> Outage.fields()
            ['start', 'finish', 'before', 'after', 'meta']

        Returns:
            list: a list of names as (:class:`str`) instances.
        """
        return list(map(attrgetter('name'), attr.fields(cls)))


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


def filter_outage_len(outages, minlen=0):
    """Filter-out outages that have a small duration.

    Args:
        outages (list): list of :class:`Outage` objects
        minlen (int): the minimum amount of seconds that the outage duration
            must have

    Yields:
        Outage: the next outage from the list that has the minimum duration.

    Example:

        >>> outages = [Outage(start=1, finish=5), Outage(start=2, finish=3)]
        >>> [o.start.timestamp for o in filter_outage_len(outages, minlen=2)]
        [1]

    """

    for o in outages:
        if (o.finish - o.start).seconds >= minlen:
            yield o


def get_outages(backend, overlap=0, minlen=0, **kwargs):
    return filter_outage_len(
        merge_outages(backend.get_outages(**kwargs), overlap=overlap),
        minlen=minlen)


def get_downtime_in_seconds(outages, start=None, finish=None):
    duration = 0
    for o in outages:
        a, b = (o.start, o.finish)
        if a:
            a = a.timestamp
        else:
            msg = 'an outage began before the filtered period'
            if start is not None:
                a = start
                log.warning(msg)
            else:
                raise ValueError(msg + ' but no start time was specified.')
        if b:
            b = b.timestamp
        else:
            msg = 'an outage ended after the filtered period'
            if finish is not None:
                b = finish
                log.warning(msg)
            else:
                raise ValueError(msg + ' but no finish time was specified.')
        assert b >= a
        duration += (b - a)
    return duration
