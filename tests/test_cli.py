# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import arrow
import pytest
from clize import errors, run
from six import StringIO
from uptime_report import cli
from uptime_report.outage import Outage


def test_nothing(mocker):
    out = StringIO()
    cli.main(args=['command'], exit=False, out=out)
    assert out.getvalue() == ''


def test_uptime(mocker):
    out = StringIO()
    cli.main(args=['command', 'uptime'], exit=False, out=out)
    assert out.getvalue() == ''


def test_version(mocker):
    mocker.patch('uptime_report.cli.get_versions')
    cli.get_versions.return_value = {'version': '1.2.3'}
    assert cli.version() == '1.2.3'
    cli.get_versions.assert_called_once()


def test_help(mocker):
    out = StringIO()
    cli.main(args=['command', '--help'], exit=False, out=out)
    assert 'Usage:' in out.getvalue()


def test_outages(capsys, mocker, ungrouped_outage_data):
    mocker.patch('uptime_report.cli.read_config')
    b = mocker.patch('uptime_report.cli.get_backend')
    impl = b.return_value.from_config.return_value
    impl.get_outages.return_value = [
        Outage(start=s, finish=f)
        for s, f in ungrouped_outage_data]
    overlap = 10800  # 3 hours
    minlen = 3700    # prune 1 hour outages
    finish = arrow.utcnow()
    start = finish.replace(hours=-1)
    cli.outages(
        start=start, finish=finish, overlap=overlap,
        minlen=minlen, fmt=cli.Format.JSON)
    impl.get_outages.assert_called_with(
        start=start, finish=finish)
    out, err = capsys.readouterr()
    assert json.loads(out) == [
        {'after': None,
         'before': None,
         'finish': '2017-07-06T20:28:01+00:00',
         'meta': {},
         'start': '2017-07-06T13:28:01+00:00'},
        {'after': None,
         'before': None,
         'finish': '2017-07-08T03:28:01+00:00',
         'meta': {},
         'start': '2017-07-07T21:28:01+00:00'},
        {'after': None,
         'before': None,
         'finish': '2017-07-08T11:28:01+00:00',
         'meta': {},
         'start': '2017-07-08T09:28:01+00:00'},
        {'after': None,
         'before': None,
         'finish': '2017-07-09T03:28:01+00:00',
         'meta': {},
         'start': '2017-07-08T22:28:01+00:00'},
        {'after': None,
         'before': None,
         'finish': '2017-07-09T13:28:01+00:00',
         'meta': {},
         'start': '2017-07-09T09:28:01+00:00'},
        {'after': None,
         'before': None,
         'finish': '2017-07-10T06:28:01+00:00',
         'meta': {},
         'start': '2017-07-09T23:28:01+00:00'}
    ]


def test_with_common_args(mocker):
    mocker.patch('uptime_report.cli.requests_cache')
    mocker.patch('uptime_report.cli.logging')

    cli.logging.ERROR = 'errz'
    cli.logging.DEBUG = 'blabla'
    del cli.logging.SILENCIO

    @cli.with_common_args
    def doit():
        pass

    run(doit, args=('',), exit=False)

    cli.logging.basicConfig.assert_called_with(level='errz')

    doit(use_cache=True)
    cli.requests_cache.install_cache.assert_called_once()

    run(doit, args=('', '--log-level=debug'), exit=False)

    cli.logging.basicConfig.assert_called_with(level='blabla')

    mock_stderr = StringIO()
    run(doit, args=('', '--log-level=silencio'), exit=False, err=mock_stderr)
    assert 'Invalid log level: silencio' in mock_stderr.getvalue()


def test_get_time():
    now = arrow.utcnow().replace(microsecond=0)
    with pytest.raises(errors.CliValueError):
        cli.get_time('-')
    with pytest.raises(errors.CliValueError):
        cli.get_time('-2foo')
    assert cli.get_time('', now) == now.timestamp
    assert cli.get_time('-2d', now) == now.replace(days=-2).timestamp
    assert cli.get_time('-2y', now) == now.replace(years=-2).timestamp
    assert cli.get_time('2017-06-01') == arrow.get('2017-06-01').timestamp
    assert cli.get_time('-2') == now.replace(days=-2).timestamp
