from __future__ import print_function
import os
import pkgutil
from lazy_object_proxy import Proxy

_backends = Proxy(lambda: _find_backends())


def _find_backends():
    mods = pkgutil.iter_modules(path=[os.path.dirname(__file__)])
    return {
        name: Proxy(lambda: importer.find_module(name).load_module(name))
        for importer, name, is_pkg in mods if not is_pkg
    }


def get_backend(name):
    return _backends[name].backend


def list_backends():
    return _backends.keys()


def backend_config(backend, config=None):
    items = []
    for name, value in backend.defaults():
        if config and name in config:
            value = config[name]
        items.append((name, value))
    return items
