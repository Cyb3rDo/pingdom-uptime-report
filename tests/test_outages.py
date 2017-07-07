from __future__ import unicode_literals

from uptime_report.outage import Outage, merge_outages


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
