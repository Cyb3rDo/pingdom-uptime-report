"""uptime_report backends.

This package contains generic backend code as well as implementations of
backends.
"""
from __future__ import print_function
import os
import pkgutil

from functools import partial
from lazy_object_proxy import Proxy


def _find_backends():
    mods = pkgutil.iter_modules(path=[os.path.dirname(__file__)])
    for importer, name, is_pkg in mods:
        if not is_pkg:
            yield (name, importer.find_module(name))


def _load_backends():
    return {
        name: Proxy(partial(loader.load_module, name))
        for name, loader in _find_backends()
    }


_BACKENDS = Proxy(_load_backends)


def get_backend(name):
    return _BACKENDS[name].backend


def list_backends():
    return _BACKENDS.keys()


def backend_config(backend, config=None):
    items = []
    for name, value in backend.defaults():
        if config and name in config:
            value = config[name]
        items.append((name, value))
    return items
