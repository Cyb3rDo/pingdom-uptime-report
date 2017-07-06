from __future__ import unicode_literals

from uptime_report.backend_utils import group_by_range, offset_iter


def test_offset_iter_none(mocker):
    method = mocker.Mock()
    method.return_value = []
    assert list(offset_iter(method)) == []
    method.assert_called_once()


def test_offset_iter_limit(mocker):
    method = mocker.Mock()
    method.side_effect = [list(range(10))]
    assert list(offset_iter(method, limit=10)) == list(range(10))
    assert method.call_args_list == [
        ({'limit': 10, 'offset': 0},),
        ({'limit': 10, 'offset': 10},),
    ]


def test_offset_iter_two(mocker):
    method = mocker.Mock()
    method.side_effect = [list(range(10)), list(range(10, 13))]
    assert list(offset_iter(method, limit=10)) == list(range(13))
    assert method.call_args_list == [
        ({'limit': 10, 'offset': 0},),
        ({'limit': 10, 'offset': 10},),
    ]


def test_offset_iter_kwargs(mocker):
    method = mocker.Mock()
    method.side_effect = []
    it = offset_iter(method, limit=10, foo='bar')
    assert list(it) == []
    method.assert_called_once_with(limit=10, offset=0, foo='bar')


def test_offset_iter_args(mocker):
    method = mocker.Mock()
    method.side_effect = []
    it = offset_iter(method, 123, limit=10)
    assert list(it) == []
    method.assert_called_once_with(123, limit=10, offset=0)


def test_group_by_range(result_data, range_data):
    ranges = list(group_by_range(result_data, lambda x: x[1], lambda x: x[0]))
    assert ranges == [
        ((id, False, start) if start else None,
         [(id, True, t) for t in results],
         (id, False, end) if end else None)
        for id, start, results, end in range_data]
