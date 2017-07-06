"""Pingdom backend for uptime data."""
import enum
from functools import partial

import attr
from pingdomlib import Pingdom
from six.moves import map
from uptime_report.backend_utils import group_by_range, offset_iter
from uptime_report.outage import Outage, Result, ResultType


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


def check_results(check, start=None, finish=None, *args, **kwargs):
    data = check.results(
        time_from=start, time_to=finish, *args, **kwargs)
    return map(partial(make_result, check), data['results'])


def outages_from_results(results):
    ranges = group_by_range(
        results,
        lambda r: r.type != ResultType.UP,
        lambda r: r.meta.get('probeid'))
    for before, data, after in ranges:
        first = last = None
        if before:  # beginning of an outage
            first = data[0]
        if after:   # end of an outage
            last = data[-1]
        yield Outage(
            start=first.time.timestamp if first else None,
            finish=last.time.timestamp if last else None)


@attr.s
class PingdomBackend(object):
    username = attr.ib()
    password = attr.ib()
    apikey = attr.ib()
    _connection = attr.ib(init=False)

    @_connection.default
    def new_connection(self):
        return Pingdom(
            self.username,
            self.password,
            self.apikey)

    def get_checks(self):
        return offset_iter(self._connection.getChecks)

    def get_results(self, start=None, finish=None,
                    status=None, *args, **kwargs):
        """Iterate over results in the given timeframe.

        :param start: int, timestamp
        :param finish: int, timestamp
        :param status: list, a list of uptime_report.outage.ResultType values
        """
        if status is not None:
            kwargs['status'] = ",".join(s.value for s in status)
        for check in self.get_checks():
            getter = partial(
                check_results, check, start=start, finish=finish)
            for result in offset_iter(getter, *args, **kwargs):
                yield result

    def get_outages(self, *args, **kwargs):
        results = self.get_results(*args, **kwargs)
        return outages_from_results(results)

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
