from __future__ import unicode_literals
import arrow

from uptime_report.backends import pingdom


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


def test_outages_from_results(mocker, range_data):
    """Test outages_from_results."""
    now = arrow.utcnow().replace(microsecond=0)

    probes = set()

    def mktype(f, n):
        """Mimic how pingdom reports failed tests."""
        if f:
            if n in probes:
                return pingdom.ResultType.DOWN
            probes.add(n)
            return pingdom.ResultType.UNCONFIRMED
        if n in probes:
            probes.remove(n)
        return pingdom.ResultType.UP

    results = [
        pingdom.Result(
            check='foo',
            type=mktype(f, n),
            time=now.replace(hours=t),
            meta={'probeid': n}
        )
        for n, f, t in range_data
    ]
    outages = pingdom.outages_from_results(results)
    assert [(o.start, o.finish) for o in outages] == [
        (None, results[10].time),
        (None, results[15].time),
        (results[11].time, results[11].time),
        (results[1].time, results[8].time),
        (results[23].time, results[23].time),
        (results[28].time, results[37].time),
        (results[42].time, results[42].time),
        (results[36].time, results[40].time),
        (results[31].time, results[44].time),
        (results[50].time, results[50].time),
        (results[56].time, results[56].time),
        (results[46].time, results[49].time),
        (results[55].time, results[55].time),
        (results[62].time, results[62].time),
        (results[38].time, results[64].time),
        (results[61].time, results[61].time),
        (results[73].time, results[74].time),
        (results[65].time, results[66].time),
        (results[88].time, results[88].time),
        (results[72].time, results[76].time),
        (results[82].time, None),
        (results[90].time, None),
        (results[87].time, None),
    ]
