from __future__ import unicode_literals

from six import StringIO
from uptime_report import cli


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
