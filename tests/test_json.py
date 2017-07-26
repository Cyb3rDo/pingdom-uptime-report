# -*- coding: utf-8 -*-
import json

import arrow
import pytest
from uptime_report.format.json import encoder
from uptime_report.outage import Outage


def test_encode_outage():
    s = arrow.utcnow()
    f = s.replace(hours=-1)
    o = Outage(start=s, finish=f)
    assert json.loads(json.dumps(o, indent=4, default=encoder)) == {
        'before': None, 'after': None, 'meta': {},
        'finish': f.for_json(),
        'start': s.for_json()
    }


def test_encode_outage_fail():
    s = arrow.utcnow()
    f = s.replace(hours=-1)
    o = Outage(start=s, finish=f, meta={'wut': set()})
    with pytest.raises(TypeError):
        json.dumps(o, indent=4, default=encoder)
