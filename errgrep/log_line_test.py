import io
import pytest
import queue
from unittest.mock import MagicMock, patch

from . import log_line
LogLine = log_line.LogLine

# Cheat a bit, by not actually ever using stdin
log_line.sys.stdin = io.StringIO()

@pytest.fixture(scope='function', autouse=True)
def reset_log_Line_stdin_thread():
    log_line.LogLine.stdin_read_thread = None

def test_log_line_inputs_get_to_raw_text_lines(tmp_path):
    # raw text
    l = LogLine(raw_text='hello\nworld')
    assert l.raw_text_lines == ['hello', 'world']

    # file
    file = (tmp_path / 'tmp')
    file.write_text('hello\nworld')
    l = LogLine(log_file=file)
    assert l.raw_text_lines == ['hello', 'world']

    # list of lines
    l = LogLine(raw_text_lines=['hello', 'world'])
    assert l.raw_text_lines == ['hello', 'world']

def test_log_line_other_inputs():
    l = LogLine('', line_timestamper=None, max_seconds_till_line_split=3, previous_line=4, read_from_stdin=0, next_line_index=12, allow_timestamp_format_changes=22)
    assert isinstance(l.line_timestamper, log_line.LineTimestamper)
    assert l.line_timestamper.allow_timestamp_format_changes == 22

    assert l.max_seconds_till_line_split == 3
    assert l.previous_line == 4
    assert l.read_from_stdin == 0
    assert l.next_line_index == 12

    assert l.log_message == ''
    assert l.log_line_lines == []

    l._parse = MagicMock()
    l.__init__('')
    l._parse.assert_called_once_with()

def test_log_line_dash_to_read_from_stin():
    class LogLineNoParse(LogLine):
        def _parse(*args, **kwargs):
            pass

    with patch.object(log_line, 'stdin_read_thread'):
        l = LogLineNoParse(log_file='-', read_from_stdin=False)

    assert l.read_from_stdin == True
    assert l.raw_text_lines == []

def test_iter_lines():
    l = LogLine('hello\nworld', read_from_stdin=False, max_seconds_till_line_split=.001)
    log_line.stdin_read_thread = MagicMock()
    log_line.stdin_read_thread.is_alive = lambda: True
    log_line.stdin_read_thread.lines_queue = queue.Queue()
    log_line.stdin_read_thread.lines_queue.put_nowait("hi")
    log_line.stdin_read_thread.lines_queue.put_nowait("again")
    l.read_from_stdin = True

    q = []
    g = l._iter_lines()
    for i in range(4):
        q.append(next(g))

    assert q == ['hello', 'world', 'hi', 'again']

    assert next(g) is None

    log_line.stdin_read_thread.is_alive = lambda: False

    with pytest.raises(StopIteration):
        assert next(g)

def test_parse():
    l = LogLine('', read_from_stdin=False)
    l._iter_lines = MagicMock(return_value=iter(['2020-03-01 10:00:00AM, hello first', 'hello', 'world', '2020-03-01 10:00:00AM, hello second', 'hi']))
    l._parse()
    assert l.log_message == '2020-03-01 10:00:00AM, hello first\nhello\nworld'
    assert l.log_line_lines == l.log_message.split('\n')

    l = LogLine('', read_from_stdin=False)
    l._iter_lines = MagicMock(return_value=iter(['2020-03-01 10:00:00AM, hello first', 'hello', None, '2020-03-01 10:00:00AM, hello second', 'hi']))
    l._parse()
    assert l.log_message == '2020-03-01 10:00:00AM, hello first\nhello'
    assert l.log_line_lines == l.log_message.split('\n')

    l = LogLine('', read_from_stdin=False)
    l._iter_lines = MagicMock(return_value=iter([None]))
    l._parse()
    assert l.log_message == ''
    assert l.log_line_lines == []

def test_get_next_log_line_no_remaining_lines():
    l = LogLine('', read_from_stdin=False)
    l.raw_text_lines = []
    l.log_line_lines = []
    assert l.get_next_log_line() is None

def test_get_next_log_line_stdin_read_is_dead():
    l = LogLine('', read_from_stdin=False)
    l.raw_text_lines = []
    l.log_line_lines = []
    l.read_from_stdin = True
    l.stdin_read_thread = MagicMock()
    l.stdin_read_thread.is_alive = MagicMock(return_value=False)
    assert l.get_next_log_line() is None

def test_get_next_log_line_vars_passed_properly():
    l = log_line.LogLine('', read_from_stdin=False)
    l.raw_text_lines = ['hello', 'world']
    l.log_line_lines = ['hello']

    l.read_from_stdin = 92
    l.line_timestamper = 22

    with patch.object(log_line, 'LogLine', return_value=2) as LogLine:
        assert l.get_next_log_line() == 2

    LogLine.assert_called_once_with(raw_text_lines=['hello', 'world'],
                                    previous_line=l,
                                    read_from_stdin=l.read_from_stdin,
                                    line_timestamper=l.line_timestamper,
                                    next_line_index=1
                                    )

def test_iter_log_lines_with_regex_1():
    l = LogLine('', read_from_stdin=False)
    l.log_message = 'hello world'

    l.get_next_log_line = MagicMock(return_value=None)
    r = [a for a in l.iter_log_lines_with_regex('HELLO', ignore_case=True)]
    l.get_next_log_line.assert_called_once_with()

    assert len(r) == 1
    assert r[0] == l

    l.get_next_log_line = MagicMock(return_value=None)
    r = [a for a in l.iter_log_lines_with_regex('HELLO', ignore_case=False)]
    l.get_next_log_line.assert_called_once_with()
    assert len(r) == 0

def test_iter_log_lines_with_regex_2():
    l1 = LogLine('', read_from_stdin=False)
    l1.log_message = 'hello world'

    l2 = LogLine('', read_from_stdin=False)
    l2.log_message = 'hello again'

    l1.get_next_log_line = MagicMock(return_value=l2)
    r = [a for a in l1.iter_log_lines_with_regex('world', ignore_case=True)]
    assert len(r) == 1
    assert r[0] == l1

    l1.get_next_log_line = MagicMock(return_value=l2)
    r = [a for a in l1.iter_log_lines_with_regex('hello', ignore_case=True)]
    assert len(r) == 2
    assert r[0] == l1
    assert r[1] == l2
