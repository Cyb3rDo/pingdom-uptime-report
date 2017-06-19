from __future__ import unicode_literals

import versioneer
from six import StringIO
from uptime_report import cli


def test_version(mocker):
    mocker.patch('versioneer.get_version')
    versioneer.get_version.return_value = '1.2.3'
    assert cli.version() == '1.2.3'
    versioneer.get_version.assert_called_once()


def test_help(mocker):
    out = StringIO()
    cli.main(args=['command', '--help'], exit=False, out=out)
    assert 'Usage:' in out.getvalue()
