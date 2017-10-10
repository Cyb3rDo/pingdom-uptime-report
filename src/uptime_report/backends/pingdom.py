# -*- coding: utf-8 -*-
"""Pingdom backend for uptime data."""
import enum
import logging
from functools import partial

import arrow
import attr
from attr.validators import in_
from pingdomlib import Pingdom
from sigtools import wrappers
from six.moves import map
from uptime_report.backend_utils import group_by_range, offset_iter
from uptime_report.outage import Outage

log = logging.getLogger(__name__)


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


class PingdomStatus(enum.Enum):
    UP = "up"
    DOWN = "down"
    UNCONFIRMED = "unconfirmed_down"
    UNKNOWN = "unknown"

    def to_result(self):
        if self.value == "unconfirmed_down":
            return ResultType.UNCONFIRMED
        return ResultType(self.value)


def make_result(check, item):
    return Result(
        time=item.get('time'),
        meta={
            'probeid': item.get('probeid'),
            'desc': item.get('statusdesc'),
        },
        check=check,
        type=PingdomStatus(item.get('status')).to_result(),
    )


@attr.s
class MaxOffsetReached(Exception):
    offset = attr.ib()


@wrappers.decorator
def continue_offset(wrapped, *args, **kwargs):
    result = None
    retries = 0
    while True:
        try:
            for result in wrapped(*args, **kwargs):
                yield result
            break
        except MaxOffsetReached:
            if retries == 3 or not result:
                raise Exception("Too much data!")
            retries += 1
            kwargs['start'] = result.time.shift(seconds=1)


def check_results(check, start=None, finish=None, *args, **kwargs):
    if 'offset' in kwargs and kwargs['offset'] > 43200:
        raise MaxOffsetReached(kwargs['offset'])
    data = check.results(
        time_from=start, time_to=finish, *args, **kwargs)
    return map(partial(make_result, check), data['results'])


def outages_from_results(results, group_by=None):
    ranges = group_by_range(
        results,
        lambda r: r.type == ResultType.DOWN,
        group_by)
    for after, data, before in ranges:
        if before and before.type == ResultType.UNCONFIRMED:
            data.append(before)  # include the unconfirmed down
        first = data[-1]
        last = data[0]
        log.debug("found outage between %s and %s: %s", first, last, data)
        meta = {}   # set up groups for this outage
        if group_by:
            meta = {'group': group_by(data[0])}
        yield Outage(
            start=first.time,
            finish=last.time,
            before=before.time if before else None,
            after=after.time if after else None,
            meta=meta)


@attr.s
class PingdomBackend(object):
    username = attr.ib()
    password = attr.ib()
    apikey = attr.ib()
    include_ok = attr.ib(default=False)
    _connection = attr.ib(init=False)

    @_connection.default
    def new_connection(self):
        return Pingdom(
            self.username,
            self.password,
            self.apikey)

    def get_checks(self):
        return offset_iter(self._connection.getChecks)

    @continue_offset
    def get_results(self, start=None, finish=None,
                    status=None, checks=None, *args, **kwargs):
        """Iterate over results in the given timeframe.

        :param start: int, timestamp
        :param finish: int, timestamp
        :param status: list, a list of uptime_report.outage.ResultType values
        :param checks: list, a list of check IDs
        """
        if status is not None:
            kwargs['status'] = ",".join(s.value for s in status)
        for check in self.get_checks():
            if checks and check.id not in checks:
                continue
            log.debug("%s: processing check %s", self, check)
            getter = partial(
                check_results, check, start=start, finish=finish)
            n = 0
            for n, result in enumerate(offset_iter(getter, *args, **kwargs)):
                yield result

            log.debug("%s: processed check %s: %s results", self, check, n)

    def get_outages(self, *args, **kwargs):
        results = self.get_results(checks=[173494], *args, **kwargs)
        for outage in outages_from_results(results):
            if outage.after and self.include_ok:
                outage.finish = outage.after
            yield outage

    @classmethod
    def defaults(cls):
        for a in sorted(attr.fields(cls), key=lambda f: f.name):
            if not a.init:
                continue
            yield (a.name, None if a.default == attr.NOTHING else a.default)

    @classmethod
    def from_config(cls, config=None):
        return cls(**{a: config[a] for a, _ in cls.defaults() if a in config})


backend = PingdomBackend
