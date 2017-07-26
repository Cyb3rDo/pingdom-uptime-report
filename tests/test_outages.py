# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from uptime_report.outage import (Outage, get_downtime_in_seconds, get_outages,
                                  merge_outages)


def test_merge_outages(outage_data):
    outages = [Outage(start=o[1], finish=o[2])
               for o in outage_data]

    merged = [(o.start.timestamp if o.start else None,
               o.finish.timestamp if o.finish else None)
              for o in merge_outages(outages)]
    assert merged == [
        (1499336881, 1499351281),
        (1499358481, 1499362081),
        (1499372881, 1499372881),
        (1499452081, 1499466481),
        (1499470081, 1499563681),
        (1499567281, 1499570881),
        (1499592481, 1499606881),
        (1499642881, 1499668081),
    ]


def test_merge_outages_open(outage_data):
    outages = [Outage(start=o[1], finish=o[2])
               for o in outage_data]

    outages[3].start = None
    outages[-3].finish = None

    merged = [(o.start.timestamp if o.start else None,
               o.finish.timestamp if o.finish else None)
              for o in merge_outages(outages)]
    assert merged == [
        (None, 1499466481),
        (1499470081, 1499563681),
        (1499567281, 1499570881),
        (1499592481, 1499606881),
        (1499642881, None),
    ]


def test_merge_outages_overlap(outage_data):
    outages = [Outage(start=o[1], finish=o[2])
               for o in outage_data]

    merged = [(o.start.timestamp if o.start else None,
               o.finish.timestamp if o.finish else None)
              for o in merge_outages(outages, overlap=4000)]
    assert merged == [
        (1499336881, 1499351281),
        (1499358481, 1499362081),
        (1499372881, 1499372881),
        (1499452081, 1499570881),
        (1499592481, 1499606881),
        (1499642881, 1499668081),
    ]


def test_get_downtime(outage_data):
    assert get_downtime_in_seconds([]) == 0
    outages = [Outage(start=o[1], finish=o[2])
               for o in outage_data]
    assert get_downtime_in_seconds(outages) == 190800
    outages = [Outage(start=o[1], finish=o[2])
               for o in outage_data]

    outages[3].start = None
    with pytest.raises(ValueError):
        assert get_downtime_in_seconds(outages)
    assert get_downtime_in_seconds(outages, start=0) == 1499642881

    outages[-3].finish = None
    with pytest.raises(ValueError):
        assert get_downtime_in_seconds(outages, start=0)
    assert get_downtime_in_seconds(
        outages, start=0, finish=outages[-1].finish.timestamp) == 1499646481


def test_get_outages_empty(mocker):
    backend = mocker.Mock()
    backend.get_outages.return_value = []
    ret = list(get_outages(backend, overlap=300, minlen=5, foo='bar'))
    backend.get_outages.assert_called_with(foo='bar')
    assert ret == []
