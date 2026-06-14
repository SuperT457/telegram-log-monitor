from collections import defaultdict

def new_cache_entry():
    return {
        'city': '',
        'region': ''
    }

class Cache:
    def __init__(self):
        self.last_pos = 0
        self.ip_cache = defaultdict(new_cache_entry)
