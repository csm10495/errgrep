import functools
import pathlib
import queue
import re
import sys
import time
import typing

from .line_timestamper import LineTimestamper
from .non_blocking_read_thread import NonBlockingReadThread

class LogLine:
    stdin_read_thread = None

    def __init__(self, raw_text=None, raw_text_lines=None,
                 log_file=None, read_from_stdin=False, previous_line:typing.Optional[typing.TypeVar('LogLine')]=None,
                 line_timestamper:typing.Optional[LineTimestamper]=None, max_seconds_till_line_split=1):
        '''
        If a - is given as the log_file, will read from stdin, (and ignore read_from_stdin)
        '''

        if (raw_text and log_file and raw_text_lines and read_from_stdin) or \
           (raw_text is None and log_file is None and raw_text_lines is None and read_from_stdin is False):
            raise ValueError("Please provide either raw_text or log_file or raw_text_lines... \
not more or less than one. Or we can use read_from_stdin without one of the others.")

        # splitlines() is slow on big inputs... try to minimize how often we do it

        self.raw_text_lines = []
        self.read_from_stdin = read_from_stdin

        if raw_text_lines:
            self.raw_text_lines = raw_text_lines
        elif raw_text:
            self.raw_text_lines = raw_text.splitlines()
        elif log_file:
            if log_file == '-':
                self.read_from_stdin = True
            else:
                self.raw_text_lines = pathlib.Path(log_file).read_text().splitlines()

        # We can read_from_stdin AFTER raw_text_lines
        if self.read_from_stdin and (self.stdin_read_thread is None or not self.stdin_read_thread.is_alive()):
            self.stdin_read_thread = NonBlockingReadThread(sys.stdin)
            self.stdin_read_thread.start()

        # when reading from stdin, we wait at most this much time before assuming a log line split
        self.max_seconds_till_line_split = max_seconds_till_line_split

        self.timestamp = None
        self.log_line_lines = []
        self.log_message = ''
        self.previous_line = previous_line

        self.line_timestamper = line_timestamper or LineTimestamper()

        self._parse()

    def _iter_lines(self):
        ''' yields a line from the given place... if it yields a None, assume that a line break happened '''
        if self.raw_text_lines:
            for line in self.raw_text_lines:
                yield line

        if self.read_from_stdin:
            break_force_time = time.time() + self.max_seconds_till_line_split
            while self.stdin_read_thread.is_alive():
                try:
                    line = self.stdin_read_thread.lines_queue.get_nowait()
                    self.raw_text_lines.append(line)
                    break_force_time = time.time() + self.max_seconds_till_line_split
                    yield line
                except queue.Empty:
                    if time.time() > break_force_time:
                        break_force_time = time.time() + self.max_seconds_till_line_split
                        yield None

                time.sleep(.001)

    def _parse(self):
        self.log_line_lines = []
        # Key Assumption:
        # All lines without timestamp are part of this log statement
        for line in self._iter_lines():

            if line is None:
                # force a line break right now... timestamp should be set from earlier on
                break

            timestamp = self.line_timestamper.coerce_datetime_from_line(line)
            if timestamp:
                if len(self.log_line_lines) == 0:
                    self.timestamp = timestamp
                    self.log_line_lines.append(line)
                else:
                    # new timestamp means we're done
                    break
            else:
                self.log_line_lines.append(line)

        self.log_message = '\n'.join(self.log_line_lines)

    @functools.lru_cache(maxsize=100)
    def get_next_log_line(self) -> typing.Optional[typing.TypeVar('LogLine')]:
        '''
        Returns the next LogLine in the log.
            Returns None if there is no more available
        '''
        lines = self.raw_text_lines[len(self.log_line_lines):]

        if lines or (self.read_from_stdin and self.stdin_read_thread.is_alive()):
            return LogLine(raw_text_lines=lines,
                           previous_line=self,
                           read_from_stdin=self.read_from_stdin,
                           line_timestamper=self.line_timestamper)

    def iter_log_lines_with_regex(self, regex, ignore_case=True):
        '''
        Goes through all LogLines checking if the message matches the regex. For each that,
            matches, yields the matching LogLine.
        '''
        current_line = self

        regex_c = re.compile(regex, flags=re.IGNORECASE if ignore_case else 0)
        # walk through all lines
        while current_line is not None:
            if re.findall(regex_c, current_line.log_message):
                yield current_line
            current_line = current_line.get_next_log_line()

