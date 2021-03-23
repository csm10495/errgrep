import datetime
import dateutil.parser
import functools
import typing

from .lra_dict import LeastRecentlyAddedDict

# max possible... we work down to figure out the right number and then cache it
MAX_TYPE_1_LENGTH = 10

class LineTimestamper:
    '''
    An object used to grab a timestamp from a given line
    '''
    line_to_datetime_cache = LeastRecentlyAddedDict(50)

    def __init__(self, allow_timestamp_format_changes:bool=False):
        self.prefered_datetime_coerce_index = None
        self.allow_timestamp_format_changes = allow_timestamp_format_changes

        # for type 1 only
        self._last_type_1_length = MAX_TYPE_1_LENGTH

    @functools.lru_cache(maxsize=1024)
    def _coerce_datetime_from_line_0(self, line:str) -> typing.Optional[datetime.datetime]:
        # date time, STUFF
        try:
            return dateutil.parser.parse(line.split(',')[0])
        except:
            pass

    @functools.lru_cache(maxsize=1024)
    def _coerce_datetime_from_line_1(self, line:str) -> typing.Optional[datetime.datetime]:
        # date time STUFF
        # works with up to MAX_TYPE_1_LENGTH items
        def doIt(line, length):
            try:
                return dateutil.parser.parse(' '.join(line.split(' ')[:length]))
            except:
                pass

        result = doIt(line, self._last_type_1_length)
        if result is not None:
            return result

        for length in range(MAX_TYPE_1_LENGTH, 0, -1):
            if length == self._last_type_1_length:
                continue

            result = doIt(line, length)
            if result is not None:
                self._last_type_1_length = length
                return result

    @functools.lru_cache(maxsize=1024)
    def _coerce_datetime_from_line_2(self, line:str) -> typing.Optional[datetime.datetime]:
        # [ seconds_since_boot ]
        # used by things like dmesg
        if line.startswith('[') and ']' in line:
            try:
                seconds = float(line.split('[', 1)[1].split(']', 1)[0])
            except:
                pass
            else:
                return datetime.datetime.fromtimestamp(seconds)

    @functools.lru_cache(maxsize=1024)
    def _get_datetime_from_line_coercion_function(self, idx:int):
        func = getattr(self, f'_coerce_datetime_from_line_{idx}')
        return func

    def coerce_datetime_from_line(self, line:str) -> typing.Optional[datetime.datetime]:
        '''
        Returns a datetime.datetime if a timestamp can be parsed from the given line.
            Otherwise returns None.
        '''
        line = line.strip()

        # coercion is slow... cache recent things
        if line in self.line_to_datetime_cache:
            return self.line_to_datetime_cache[line]

        if self.prefered_datetime_coerce_index is not None:
            func = self._get_datetime_from_line_coercion_function(self.prefered_datetime_coerce_index)
            result = func(line)
            if result:
                self.line_to_datetime_cache[line] = result
                return result

        if self.allow_timestamp_format_changes or self.prefered_datetime_coerce_index is None:
            # change this number if we add a coercion mechanism
            for idx in range(3):
                if idx != self.prefered_datetime_coerce_index:
                    func = self._get_datetime_from_line_coercion_function(idx)
                    result = func(line)
                    if result:
                        self.prefered_datetime_coerce_index = idx
                        self.line_to_datetime_cache[line] = result
                        return result