
class LeastRecentlyAddedDict(dict):
    '''
        A simple dict that will automatically remove key/values once we have more
            than the given number of keys
    '''

    def __init__(self, max_keys):
        '''
        Initializer that specifies the max number of keys in the dict before auto-cleaning
        '''
        dict.__init__(self)
        self._max_keys = max_keys

    def __setitem__(self, key, value):
        '''
        Called when an item is set in the dict
        '''
        dict.__setitem__(self, key, value)

        while len(self) > self._max_keys:
            self.pop(next(iter(self)))
