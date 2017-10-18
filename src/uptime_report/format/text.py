# -*- coding: utf-8 -*-
from __future__ import absolute_import


def write_text(out, data, **_):
    for obj in data:
        try:
            obj = obj.humanize()
        except AttributeError:
            obj = obj.for_json()
        out.write("\n".join(
            "{}: {}".format(k, obj[k]) for k in sorted(obj)))
        out.write("\n")


Writer = write_text
