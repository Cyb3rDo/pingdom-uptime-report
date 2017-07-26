# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json


def encoder(obj):
    try:
        return obj.for_json()
    except AttributeError:
        raise TypeError(repr(obj) + " is not JSON serializable")


def write_json(out, data, **_):
    json.dump(list(data), out, indent=4, default=encoder)


Writer = write_json
