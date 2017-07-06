from __future__ import unicode_literals
import arrow
import pytest

from uptime_report.backends import pingdom


@pytest.fixture
def pingdom_result_data(result_data):
    """A list of raw pingdom results."""
    seen = set()

    def mktype(down, n):
        """Mimic how pingdom reports failed tests."""
        if down:
            if n in seen:
                return 'down'
            seen.add(n)
            return 'unconfirmed'
        if n in seen:
            seen.remove(n)
        return 'up'

    return [
        {
            'check': 'foo',
            'type':  mktype(down, n),
            'time': t,
            'meta': {'probeid': n}
        }
        for n, down, t in result_data
    ]


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


def test_outages_from_results(mocker, pingdom_result_data, outage_data):
    """Test outages_from_results."""
    results = [
        pingdom.Result(
            check=d['check'],
            type=pingdom.ResultType(d['type']),
            time=d['time'],
            meta=d['meta']
        )
        for d in pingdom_result_data
    ]
    outages = pingdom.outages_from_results(results)

    assert outage_data == [
        (o.start.timestamp if o.start else None,
         o.finish.timestamp if o.finish else None)
        for o in outages
    ]
