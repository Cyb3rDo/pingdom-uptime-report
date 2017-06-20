"""Pingdom backend for uptime data."""
import attr
from six.moves import map
from uptime_report.backends import Backend, Check
from uptime_report.outage import Outage, OutageType
from pingdomlib import Pingdom


@attr.s
class PingdomCheck(Check):
    inner = attr.ib()

    def _make_outage(self, outage):
        kwargs = {
            'start': outage['timefrom'],
            'finish': outage['timeto'],
            'check': self
        }
        try:
            kwargs['type'] = OutageType(outage.get('status'))
        except ValueError:
            pass
        return Outage(**kwargs)

    def _list_outages(self, start, finish):
        return self.inner.outages(time_from=start, time_to=finish)

    def run(self, start=None, finish=None, **kwargs):
        return map(self._make_outage, self._list_outages(start, finish))


class PingdomBackend(Backend):
    name = 'pingdom'

    check_cls = PingdomCheck

    config_keys = ['user', 'pass', 'key', 'checks']

    @property
    def connection(self):
        if not hasattr(self, 'connection'):
            self.connection = Pingdom(
                self.config.get('user'),
                self.config.get('pass'),
                self.config.get('key'))
        return self.connection

    def list_checks(self):
        return map(self.check_cls, self.connection.getChecks())
