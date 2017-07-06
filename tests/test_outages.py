from __future__ import unicode_literals

from uptime_report.outage import Outage, merge_outages


def test_merge_outages(outage_data):
    outages = [Outage(start=o[0], finish=o[1])
               for o in outage_data]

    merged = [(o.start.timestamp if o.start else None,
               o.finish.timestamp if o.finish else None)
              for o in merge_outages(outages)]
    assert merged == [
        (None, 1499387281),
        (1499416081, 1499416081),
        (1499434081, 1499563681),
        (1499567281, 1499570881),
        (1499592481, 1499606881),
        (1499628481, None)
    ]
