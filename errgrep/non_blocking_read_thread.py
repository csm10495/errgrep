import queue
import sys
import threading
import time

class NonBlockingReadThread(threading.Thread):
    '''
    A thread that continually reads lines from a file object and places each read line in
        .lines_queue

    This runs as a daemon thread and should be considered a singleton for a given file_like_obj.
    '''
    lines_queue: queue.Queue = queue.Queue()
    def __init__(self, file_like_obj):
        self.file_like_obj = file_like_obj
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        for line in self.file_like_obj:
            line = line.rstrip('\r\n')
            self.lines_queue.put_nowait(line)

        while not self.lines_queue.empty():
            time.sleep(.01)

class StdinReadThread(NonBlockingReadThread):
    ''' A NonBlockingReadThread for stdin '''
    def __init__(self):
        NonBlockingReadThread.__init__(self, sys.stdin)

    def start_if_not_started_yet(self):
        try:
            NonBlockingReadThread.start(self)
        except RuntimeError:
            pass

stdin_read_thread = StdinReadThread()
