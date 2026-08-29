from collections import defaultdict

def new_cache_entry():
    return {
        'city': '',
        'region': ''
    }

class Cache:
    def __init__(self):
        # position of I/O pointer in the log file, used by seek() function
        self.last_pos = 0

        # dictionary of already-queried IP addresses
        # used to cache some IP-related information
        self.ip_cache = defaultdict(new_cache_entry)
