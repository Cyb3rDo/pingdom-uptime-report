import attr
import os
import pkgutil
from sigtools import modifiers


_backends = None


def get_subclasses(cls):
    for klass in cls.__subclasses__():
        for subclass in get_subclasses(klass):
            yield subclass
        yield klass


def _load_backends():
    global _backends
    mods = pkgutil.iter_modules(path=[os.path.dirname(__file__)])
    for importer, name, is_pkg in mods:
        importer.find_module(name).load_module(name)
    _backends = {klass.name: klass for klass in get_subclasses(Backend)}


def get_backend(name):
    if _backends is None:
        _load_backends()
    return _backends[name]


def list_backends():
    if _backends is None:
        _load_backends()
    return _backends.keys()


def backend_config(backend, config=None):
    keys = getattr(backend, 'config_keys', [])
    cfg = config if config else dict.fromkeys(keys)
    return [(k, cfg[k]) for k in keys if k in cfg]


class Check(object):
    """Base check class."""

    @modifiers.kwoargs('start', 'finish')
    def run(self, start=None, finish=None, **kwargs):
        raise NotImplementedError("Must implement .run().")


@attr.s
class Backend(object):
    """Base backend class."""
    config = attr.ib(default={})

    def list_checks(self):
        raise NotImplementedError("Must implement .list_checks().")
