import datetime
import dateutil.parser
import pytest

from errgrep.line_timestamper import LineTimestamper

@pytest.fixture(scope='function', autouse=True)
def reset_line_to_datetime_cache():
    LineTimestamper.line_to_datetime_cache.clear()

def test_timestamp_type_0():
    line = '2020-03-01 10:00:00AM, Log line'
    l = LineTimestamper()
    assert l.coerce_datetime_from_line(line) == dateutil.parser.parse('2020-03-01 10:00:00AM')
    assert l.prefered_datetime_coerce_index == 0

def test_timestamp_type_0_alt():
    line = '2020-03-01 10:00:00AM'
    l = LineTimestamper()
    assert l.coerce_datetime_from_line(line) == dateutil.parser.parse('2020-03-01 10:00:00AM')
    assert l.prefered_datetime_coerce_index == 0

def test_timestamp_type_1():
    line = '2020-03-01 10:00:00AM Log line'
    l = LineTimestamper()
    assert l.coerce_datetime_from_line(line) == dateutil.parser.parse('2020-03-01 10:00:00AM')
    assert l.prefered_datetime_coerce_index == 1
    assert l._last_type_1_length == 2

def test_timestamp_type_1_alt():
    line = 'Thu Mar 18 08:49:48 2020 hello world'
    l = LineTimestamper()
    assert l.coerce_datetime_from_line(line) == dateutil.parser.parse('Thu Mar 18 08:49:48 2020')
    assert l.prefered_datetime_coerce_index == 1
    assert l._last_type_1_length == 5

def test_timestamp_type_2():
    line = '[1234] log line'
    l = LineTimestamper()
    assert l.coerce_datetime_from_line(line) == datetime.datetime.fromtimestamp(1234)
    assert l.prefered_datetime_coerce_index == 2

def test_timestamp_without_a_timestamp():
    line = ' , log line without timestamp'
    l = LineTimestamper()
    assert l.coerce_datetime_from_line(line) is None

def test_timestamp_allow_timestamp_format_changes_false():
    l = LineTimestamper(allow_timestamp_format_changes=False)
    assert l.coerce_datetime_from_line('[100]]') is not None
    assert l.coerce_datetime_from_line('2020-03-01 10:00:00AM Log line') is None

def test_timestamp_allow_timestamp_format_changes_true():
    l = LineTimestamper(allow_timestamp_format_changes=True)
    assert l.coerce_datetime_from_line('2020-03-01 10:00:00AM, Log line') is not None
    assert l.coerce_datetime_from_line('2020-03-01 10:00:00AM Log line') is not None
