from watchdog.events import FileSystemEventHandler

"""
Watchdog handler for filesystem events

Watchdog operates on a separate, independent thread;
this class serves as a bridge between Watchdog thread and asyncio loop,
sending a notification to process the log file when it is modified
"""
class LogHandler(FileSystemEventHandler):
    def __init__(self, loop, queue, monitored_path):
        # Asyncio loop
        self.loop = loop
        
        # Queue to which notifications are routed
        self.queue = queue

        # log path monitored 
        self.monitored_path = monitored_path

    def on_modified(self,event):
        # check that modified file is the actual monitored one
        if event.src_path == self.monitored_path:
            self.loop.call_soon_threadsafe(
                self.queue.put_nowait,
                None
            )
