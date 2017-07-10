# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import arrow
import pytest
from uptime_report.backends import pingdom


@pytest.fixture
def pingdom_results(result_data):
    """A list of raw pingdom results."""

    def mktype(down):
        """Mimic how pingdom reports failed tests."""
        while True:
            while not down:
                down = yield pingdom.ResultType.UP
            down = yield pingdom.ResultType.UNCONFIRMED
            while down:
                down = yield pingdom.ResultType.DOWN
    mkt = mktype(False)
    mkt.send(None)

    data = [pingdom.Result(check='foo',
                           type=mkt.send(down),
                           time=t,
                           meta={'probeid': n})
            for n, down, t in result_data]
    return reversed(data)


def test_pingdom_status():
    """Test PingdomStatus normalizes the unconfirmed status."""
    unconfirmed = pingdom.PingdomStatus.UNCONFIRMED.to_result()
    assert unconfirmed == pingdom.ResultType.UNCONFIRMED
    assert pingdom.PingdomStatus.UP.to_result() == pingdom.ResultType.UP


def test_new_connection(mocker):
    """Test PingdomBackend forwards parameters to PingdomLib."""
    mocker.patch('uptime_report.backends.pingdom.Pingdom')
    pingdom.PingdomBackend('user', 'pass', 'key')
    pingdom.Pingdom.assert_called_once_with('user', 'pass', 'key')


def test_get_checks(mocker):
    """Test .get_checks()."""
    mocker.patch('uptime_report.backends.pingdom.Pingdom')
    b = pingdom.PingdomBackend('user', 'pass', 'key')
    pingdom.Pingdom.return_value.getChecks.side_effect = [range(3)]
    assert list(b.get_checks()) == list(range(3))


def test_get_no_results(mocker):
    """Test .get_results with no results."""
    finish = arrow.utcnow()
    start = finish.replace(days=-30)
    mocker.patch('uptime_report.backends.pingdom.Pingdom')
    b = pingdom.PingdomBackend('user', 'pass', 'key')
    check = mocker.Mock()
    check.results.side_effect = [{'results': []}]
    pingdom.Pingdom.return_value.getChecks.side_effect = [[check]]
    it = b.get_results(start=start.timestamp, finish=finish.timestamp)
    results = list(it)
    check.results.assert_called_once_with(
        offset=0, limit=1000,
        time_from=start.timestamp, time_to=finish.timestamp
    )
    assert len(results) == 0


def test_get_result_status(mocker):
    """Test .get_results with a status filter."""
    finish = arrow.utcnow()
    start = finish.replace(days=-30)
    mocker.patch('uptime_report.backends.pingdom.Pingdom')
    b = pingdom.PingdomBackend('user', 'pass', 'key')
    check = mocker.Mock()
    check.results.side_effect = [{'results': []}]
    pingdom.Pingdom.return_value.getChecks.side_effect = [[check]]
    it = b.get_results(
        start=start.timestamp, finish=finish.timestamp,
        status=[pingdom.ResultType.DOWN, pingdom.ResultType.UP])
    results = list(it)
    check.results.assert_called_once_with(
        offset=0, limit=1000,
        time_from=start.timestamp, time_to=finish.timestamp,
        status="down,up"
    )
    assert len(results) == 0


def test_get_results(mocker):
    """Test .get_results with a result."""
    finish = arrow.utcnow()
    start = finish.replace(days=-30)
    mocker.patch('uptime_report.backends.pingdom.Pingdom')
    b = pingdom.PingdomBackend('user', 'pass', 'key')
    check = mocker.Mock()
    data = {
        'time': start.timestamp,
        'probeid': 1,
        'status': 'down'
    }
    check.results.side_effect = [{'results': [data]}]
    pingdom.Pingdom.return_value.getChecks.side_effect = [[check]]
    it = b.get_results(start=start.timestamp, finish=finish.timestamp)
    results = list(it)
    check.results.assert_called_once_with(
        offset=0, limit=1000,
        time_from=start.timestamp, time_to=finish.timestamp
    )
    assert len(results) == 1
    assert results[0].time.timestamp == data['time']
    assert results[0].meta == {'probeid': data['probeid'], 'desc': None}
    assert results[0].check == check
    assert results[0].type == pingdom.ResultType.DOWN


def test_get_max_results(mocker):
    """Test .get_results with more than the maximum number."""
    finish = arrow.utcnow()
    start = finish.replace(days=-30)
    mocker.patch('uptime_report.backends.pingdom.Pingdom')
    b = pingdom.PingdomBackend('user', 'pass', 'key')
    check = mocker.Mock()
    data = {
        'time': start.timestamp,
        'probeid': 1,
        'status': 'down'
    }
    check.results.side_effect = [{'results': [data] * 1000}] * 45
    pingdom.Pingdom.return_value.getChecks.side_effect = [[check]]
    it = b.get_results(start=start.timestamp, finish=finish.timestamp)
    results = list(it)
    check.results.assert_any_call(
        offset=43000, limit=1000,
        time_from=start.timestamp, time_to=finish.timestamp
    )
    check.results.call_count = 43
    assert len(results) == 44000


def test_outages_from_results(mocker, pingdom_results, outage_data):
    """Test outages_from_results."""
    outages = list(pingdom.outages_from_results(
        pingdom_results,
        group_by=lambda r: r.meta['probeid']))
    outages.sort(key=lambda o: o.start.timestamp)

    assert outage_data == [
        (o.meta['group'],
         o.start.timestamp if o.start else None,
         o.finish.timestamp if o.finish else None)
        for o in outages
    ]


def test_outages_from_results_ungrouped(
        mocker, pingdom_results, ungrouped_outage_data):
    """Test outages_from_results without grouping by probeid."""
    outages = [(o.start.timestamp if o.start else None,
                o.finish.timestamp if o.finish else None)
               for o in pingdom.outages_from_results(pingdom_results)]
    assert list(reversed(ungrouped_outage_data)) == outages
