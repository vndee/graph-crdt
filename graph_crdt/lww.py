import time


class LWWSet:
    def __init__(self):
        self.added_set = set()
        self.removed_set = set()

        self.added_timestamp = dict()
        self.removed_timestamp = dict()

    def add(self, item: object):
        self.added_set.add(item)
        self.added_timestamp[item] = time.time()

    def remove(self, item: object):
        self.removed_set.add(item)
        self.removed_timestamp[item] = time.time()

    def free_added(self, item: object):
        self.added_set.remove(item)
        self.added_timestamp.pop(item)

    def free_removed(self, item: object):
        self.removed_set.remove(item)
        self.removed_timestamp.pop(item)
