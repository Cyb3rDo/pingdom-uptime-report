from collections import defaultdict, deque

from sigtools.modifiers import kwoargs


@kwoargs('limit', 'offset')
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
    ranges = defaultdict(deque)
    sentinels = defaultdict(lambda: deque([None], maxlen=1))

    def yielder(src):
        for item in src:
            key = keyfunc(item) if keyfunc else item
            if pred(item):
                ranges[key].append(item)
            else:
                if key in ranges:
                    yield (
                        sentinels[key][0],
                        list(ranges.pop(key)),
                        item
                    )
                sentinels[key].append(item)
        for k, r in ranges.items():
            yield (
                sentinels[k][0],
                list(r),
                None
            )
    return yielder(it)
