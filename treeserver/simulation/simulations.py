

class BaseSim(object):

    def __init__(self, uuid):
        self.uuid = uuid

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        return self.__dict__.copy()

class Robot(BaseSim):

    pass
