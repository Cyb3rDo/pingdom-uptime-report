# -*- coding: utf-8 -*-
from __future__ import absolute_import

import csv


def write_csv(fhandle, outages, fields):
    """Write a list of outages to a file as CSV.

    Example:

        >>> from six import StringIO
        >>> s = StringIO()
        >>> t = arrow.get(0)
        >>> write_outages_csv(s, [Outage(t, t)], Outage.fields())
        >>> s.getvalue()
        'start,finish,before,after,meta\\r\\n1970-01-01T00:00:00+00:00,1970-01-01T00:00:00+00:00,,,{}\\r\\n'

    Args:
        fhandle (io.TextIOWrapper): the file object to write the CSV data to
        outages (list): a list of :class:`Outage` objects to write.

    """
    writer = csv.DictWriter(fhandle, fields)
    writer.writeheader()
    writer.writerows([o.for_json() for o in outages])
