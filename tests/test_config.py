from __future__ import unicode_literals

from tests.util import TeeIO
from uptime_report.config import write_config


def test_write_config_stdout(mocker):
    mock_stdout = TeeIO()
    write_config(output=mock_stdout.as_manager())
    assert mock_stdout.getvalue() == "\n".join([
        "[pingdom]",
        "checks = None",
        "key = None",
        "pass = None",
        "user = None",
        ""])
