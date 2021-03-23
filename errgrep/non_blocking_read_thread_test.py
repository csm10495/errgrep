import io

from .non_blocking_read_thread import NonBlockingReadThread

def test_non_blocking_read_thread(tmp_path):
    file_path = tmp_path / 'tmp'
    with open(file_path, 'w') as f:
        f.write('hello\n')
        f.write('world\n')

    t = NonBlockingReadThread(open(file_path, 'r'))
    t.start()

    # shouldn't die since we didn't empty the queue
    assert t.is_alive()

    line = t.lines_queue.get()
    assert line == 'hello'

    line = t.lines_queue.get()
    assert line == 'world'

    assert t.lines_queue.empty()

    # now its empty and can die
    t.join(1)
    assert not t.is_alive()