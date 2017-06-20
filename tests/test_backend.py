from __future__ import unicode_literals

from uptime_report.backends import backend_config


def test_backend_config_nokeys(mocker):
    backend = mocker.Mock(NAME='test')
    del backend.config_keys
    assert backend_config(backend) == []


def test_backend_config_skel(mocker):
    backend = mocker.Mock(
        name='test', config_keys=['a', 'b'])
    assert backend_config(backend) == [
        ('a', None),
        ('b', None)
    ]


def test_backend_config(mocker):
    backend = mocker.Mock(
        name='test', config_keys=['a', 'b'])
    config = {'a': 'foo'}
    assert backend_config(backend, config) == [
        ('a', 'foo'),
    ]
