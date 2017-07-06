from __future__ import unicode_literals

import py.path
import pytest
from configobj import ConfigObj
from uptime_report import cli
from uptime_report.backends import backend_config, get_backend, list_backends


def test_backend_config_nokeys(mocker):
    backend = mocker.Mock(defaults=lambda: [])
    assert backend_config(backend) == []


def test_backend_config_skel(mocker):
    backend = mocker.Mock(
        defaults=lambda: [('a', None), ('b', None)])
    assert backend_config(backend) == [
        ('a', None),
        ('b', None),
    ]


def test_backend_config(mocker):
    backend = mocker.Mock(
        defaults=lambda: [('a', None), ('b', None)])
    config = {'a': 'foo'}
    assert backend_config(backend, config) == [
        ('a', 'foo'),
        ('b', None),
    ]


def test_list_backends(mocker):
    mocker.patch('uptime_report.cli.list_backends')
    cli.list_backends.return_value = ['one', 'two']
    assert cli.backends() == 'one\ntwo'
    cli.list_backends.assert_called_once()


@pytest.fixture(scope='function')
def backend(request):
    """Return a backend implementation class for this name."""
    return get_backend(request.param)


@pytest.fixture(scope='function')
def configdir(tmpdir, request):
    """Create a temp dir with all config files."""
    testdir = py.path.local(request.module.__file__).dirname
    configdir = py.path.local(testdir).join("config")
    dest = tmpdir.join(configdir.basename).mkdir()
    for f in configdir.visit():
        f.copy(dest)
    return dest


@pytest.fixture(scope='function')
def config(configdir, request):
    """Return appropriate config section for this test."""
    try:
        path = configdir.join(request.param)
        return ConfigObj(path)[request.param]
    except IOError:
        return ConfigObj()


@pytest.mark.parametrize(
    'backend,config', zip(*[list_backends()] * 2), indirect=['backend', 'config'])  # noqa
def test_from_config(backend, config):
    backend.from_config(config)
