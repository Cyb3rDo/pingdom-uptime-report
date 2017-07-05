from __future__ import unicode_literals

from uptime_report.backend_utils import offset_iter, group_by_range


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


def test_group_by_range(range_data):
    ranges = list(group_by_range(range_data, lambda x: x[1], lambda x: x[0]))
    assert ranges == [
        (None,
         [(0, True, 4), (0, True, 10)],
         (0, False, 13)),
        (None,
         [(3, True, 15)],
         (3, False, 16)),
        ((2, False, 2),
         [(2, True, 11)],
         (2, False, 17)),
        ((4, False, 0),
         [(4, True, 1), (4, True, 5), (4, True, 7), (4, True, 8)],
         (4, False, 18)),
        ((2, False, 17),
         [(2, True, 23)],
         (2, False, 25)),
        ((0, False, 13),
         [(0, True, 28), (0, True, 33), (0, True, 37)],
         (0, False, 39)),
        ((0, False, 39),
         [(0, True, 42)],
         (0, False, 43)),
        ((3, False, 34),
         [(3, True, 36), (3, True, 40)],
         (3, False, 47)),
        ((4, False, 21),
         [(4, True, 31), (4, True, 44)],
         (4, False, 51)),
        ((2, False, 45),
         [(2, True, 50)],
         (2, False, 54)),
        ((4, False, 51),
         [(4, True, 56)],
         (4, False, 57)),
        ((0, False, 43),
         [(0, True, 46), (0, True, 48), (0, True, 49)],
         (0, False, 58)),
        ((3, False, 53),
         [(3, True, 55)],
         (3, False, 60)),
        ((0, False, 59),
         [(0, True, 62)],
         (0, False, 67)),
        ((1, False, 24),
         [(1, True, 38), (1, True, 41), (1, True, 63), (1, True, 64)],
         (1, False, 68)),
        ((2, False, 54),
         [(2, True, 61)],
         (2, False, 70)),
        ((4, False, 57),
         [(4, True, 73), (4, True, 74)],
         (4, False, 83)),
        ((3, False, 60),
         [(3, True, 65), (3, True, 66)],
         (3, False, 84)),
        ((3, False, 84),
         [(3, True, 88)],
         (3, False, 94)),
        ((2, False, 70),
         [(2, True, 72), (2, True, 75), (2, True, 76)],
         (2, False, 95)),
        ((0, False, 78),
         [(0, True, 82), (0, True, 86), (0, True, 89), (0, True, 99)],
         None),
        ((1, False, 81),
         [(1, True, 90), (1, True, 93), (1, True, 96)],
         None),
        ((4, False, 85),
         [(4, True, 87), (4, True, 91), (4, True, 92)],
         None),
    ]
