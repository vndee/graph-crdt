import time


class LWWSet:
    def __init__(self):
        self.added = dict()
        self.removed = dict()

    def add(self, item: object):
        self.added[item] = time.time()

    def remove(self, item: object):
        self.removed[item] = time.time()

    def free_added(self, item: object):
        self.added.pop(item)

    def free_removed(self, item: object):
        self.removed.pop(item)
