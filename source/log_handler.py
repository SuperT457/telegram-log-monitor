# from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogHandler(FileSystemEventHandler):
    def __init__(self, loop, queue, monitored_path):
        self.loop = loop
        self.queue = queue
        self.monitored_path = monitored_path

    def on_modified(self,event):
        if event.src_path == self.monitored_path:
            self.loop.call_soon_threadsafe(
                self.queue.put_nowait,
                None
            )
