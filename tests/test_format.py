# -*- coding: utf-8 -*-
import pytest

from clize import errors
from six import StringIO
from uptime_report import format
from uptime_report.outage import Outage


def test_missing_format(mocker):
    mocker.patch('uptime_report.format.log', autospec=True)
    mocker.patch('uptime_report.format.importlib', autospec=True)
    mock_import_module = format.importlib.import_module
    mock_warning = format.log.warning

    def _checkit():
        assert format.DEFAULT_FORMAT.writer is None
        assert mock_import_module.call_count == 1
        assert mock_warning.call_count == 1
        assert format.DEFAULT_FORMAT.value in mock_warning.call_args[0]

    mock_import_module.return_value = None
    _checkit()

    mocker.resetall()
    mock_import_module.side_effect = ImportError()
    _checkit()


def test_with_format_default(mocker):

    @format.with_format
    def wrapped(fmt=None):
        assert fmt == format.DEFAULT_FORMAT

    wrapped()

    mocker.patch('uptime_report.format.importlib', autospec=True)
    mock_import_module = format.importlib.import_module
    mock_import_module.return_value = None
    with pytest.raises(errors.CliValueError):
        wrapped()


def test_outages_default(ungrouped_outage_data):
    out = StringIO()
    outages = [Outage(start=s, finish=f)
               for s, f in ungrouped_outage_data]
    format.DEFAULT_FORMAT.writer(out, outages, whatever='blabla')
    assert out.getvalue() == """\
Begin: 2017-07-06 13:28:01+00:00
Duration: an hour
End: 2017-07-06 14:28:01+00:00
Begin: 2017-07-06 16:28:01+00:00
Duration: an hour
End: 2017-07-06 17:28:01+00:00
Begin: 2017-07-06 19:28:01+00:00
Duration: an hour
End: 2017-07-06 20:28:01+00:00
Begin: 2017-07-07 21:28:01+00:00
Duration: 2 hours
End: 2017-07-07 23:28:01+00:00
Begin: 2017-07-08 01:28:01+00:00
Duration: 2 hours
End: 2017-07-08 03:28:01+00:00
Begin: 2017-07-08 09:28:01+00:00
Duration: 2 hours
End: 2017-07-08 11:28:01+00:00
Begin: 2017-07-08 16:28:01+00:00
Duration: an hour
End: 2017-07-08 17:28:01+00:00
Begin: 2017-07-08 22:28:01+00:00
Duration: 5 hours
End: 2017-07-09 03:28:01+00:00
Begin: 2017-07-09 09:28:01+00:00
Duration: 4 hours
End: 2017-07-09 13:28:01+00:00
Begin: 2017-07-09 23:28:01+00:00
Duration: 7 hours
End: 2017-07-10 06:28:01+00:00
"""


def test_outages_default_inhuman(mocker, ungrouped_outage_data):
    out = StringIO()
    outages = [Outage(start=s, finish=f)
               for s, f in ungrouped_outage_data]
    mocker.patch.object(Outage, 'humanize', autospec=True)
    del Outage.humanize
    format.DEFAULT_FORMAT.writer(out, outages, whatever='blabla')
    assert out.getvalue() == """\
after: None
before: None
finish: 2017-07-06T14:28:01+00:00
meta: {}
start: 2017-07-06T13:28:01+00:00
after: None
before: None
finish: 2017-07-06T17:28:01+00:00
meta: {}
start: 2017-07-06T16:28:01+00:00
after: None
before: None
finish: 2017-07-06T20:28:01+00:00
meta: {}
start: 2017-07-06T19:28:01+00:00
after: None
before: None
finish: 2017-07-07T23:28:01+00:00
meta: {}
start: 2017-07-07T21:28:01+00:00
after: None
before: None
finish: 2017-07-08T03:28:01+00:00
meta: {}
start: 2017-07-08T01:28:01+00:00
after: None
before: None
finish: 2017-07-08T11:28:01+00:00
meta: {}
start: 2017-07-08T09:28:01+00:00
after: None
before: None
finish: 2017-07-08T17:28:01+00:00
meta: {}
start: 2017-07-08T16:28:01+00:00
after: None
before: None
finish: 2017-07-09T03:28:01+00:00
meta: {}
start: 2017-07-08T22:28:01+00:00
after: None
before: None
finish: 2017-07-09T13:28:01+00:00
meta: {}
start: 2017-07-09T09:28:01+00:00
after: None
before: None
finish: 2017-07-10T06:28:01+00:00
meta: {}
start: 2017-07-09T23:28:01+00:00
"""
