import datetime
import dateutil.parser

from errgrep.line_timestamper import LineTimestamper

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