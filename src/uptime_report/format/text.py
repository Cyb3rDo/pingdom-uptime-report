# -*- coding: utf-8 -*-
from __future__ import absolute_import


def write_text(out, data, **_):
    for obj in data:
        try:
            obj = obj.humanize()
        except AttributeError:
            obj = obj.for_json()
        out.write("\n".join(
            ": ".join(i) for i in obj.items()))
        out.write("\n")


Writer = write_text
