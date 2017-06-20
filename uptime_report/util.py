from operator import itemgetter
from functools import reduce



def safe_get(k, obj):
    if hasattr(obj, 'get'):
        return obj.get(k)


def deep_get(k, obj):
    """Given a dotted key name, dig into a dict."""
    reduce(lambda o, i: safe_get(k, o), k.split('.'), obj)
