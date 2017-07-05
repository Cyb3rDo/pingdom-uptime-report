from __future__ import unicode_literals

from tests.util import TeeIO
from uptime_report.config import write_config


def test_write_config_stdout(mocker):
    mock_stdout = TeeIO()
    write_config(output=mock_stdout.as_manager())
    assert mock_stdout.getvalue() == b"\n".join([
        b"[pingdom]",
        b"apikey = None",
        b"password = None",
        b"username = None",
        b""])
