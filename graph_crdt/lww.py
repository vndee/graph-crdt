import time
from .utils import get_logger


logger = get_logger("LWW Set")


def try_catch(func, *args, **kwargs):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except Exception as e:
            logger.exception(e)
            return False
    return wrapper


class LWWSet:
    def __init__(self):
        self.added = dict()
        self.removed = dict()

    @try_catch
    def add(self, item: object):
        self.added[item] = time.time()

    @try_catch
    def remove(self, item: object):
        self.removed[item] = time.time()

    @try_catch
    def free_added(self, item: object):
        self.added.pop(item)

    @try_catch
    def free_removed(self, item: object):
        self.removed.pop(item)
