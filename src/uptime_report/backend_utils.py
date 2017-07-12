# -*- coding: utf-8 -*-
from collections import OrderedDict, defaultdict

from sigtools.modifiers import autokwoargs


@autokwoargs
def offset_iter(method, limit=1000, offset=0, *args, **kwargs):
    """Call a method with limit/offset arguments until exhausted.

    Given a callable that accepts limit/offset keyword arguments
    and returns an iterable, call the method repeatedly until
    less than limit items are returned, yielding each item.
    """
    previous = -limit
    o = offset
    while previous < o and not (o - previous) % limit:
        previous = o
        data = method(limit=limit, offset=o, *args, **kwargs)
        for o, result in enumerate(data, start=(o + 1)):
            yield result


def group_by_range(it, pred, keyfunc=None):
    """Return contiguous ranges of items satisfying a predicate."""
    ranges = OrderedDict()
    sentinels = defaultdict(lambda: None)
    key = "default"
    for item in it:
        key = keyfunc(item) if keyfunc else key
        if pred(item):
            ranges.setdefault(key, []).append(item)
        else:
            previous_sentinel = sentinels[key]
            next_sentinel = item
            if key in ranges:
                yield (
                    previous_sentinel,
                    list(ranges.pop(key)),
                    next_sentinel
                )
            sentinels[key] = next_sentinel
    for k, r in ranges.items():
        yield (
            sentinels[k],
            list(r),
            None
        )
