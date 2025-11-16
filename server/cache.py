import time

class Cache:
    def __init__(self, ttl=10):
        self.ttl = ttl
        self.storage = {}

    def get(self, key):
        if key in self.storage:
            value, timestamp = self.storage[key]
            if time.time() - timestamp < self.ttl:
                return value
        return None

    def set(self, key, value):
        self.storage[key] = (value, time.time())
