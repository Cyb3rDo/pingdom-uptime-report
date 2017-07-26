# -*- coding: utf-8 -*-
import arrow
import pytest
from clize import errors
from uptime_report import cli
from uptime_report.format import Format, gsheet, with_format
from uptime_report.outage import Outage


def test_outages_missing_req(mocker):
    mocker.patch('uptime_report.format.gsheet.Writer', new=None)

    @with_format
    def wrapped(fmt=None):
        pass
    with pytest.raises(errors.CliValueError):
        wrapped(fmt=Format.GSHEET)


def test_outages_gsheet(capsys, mocker, ungrouped_outage_data):
    mocker.patch('uptime_report.format.gsheet.pygsheets')
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
        minlen=minlen, fmt=Format.GSHEET, config='tests/config/pingdom')
    assert gsheet.pygsheets.authorize.call_count == 1
