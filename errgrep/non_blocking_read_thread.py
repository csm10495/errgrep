import queue
import threading
import time

class NonBlockingReadThread(threading.Thread):
    '''
    A thread that continually reads lines from a file object and places each read line in
        .lines_queue

    This runs as a daemon thread and should be considered a singleton.
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
            time.sleep(.1)