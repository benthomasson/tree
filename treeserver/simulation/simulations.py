

from simulation.models import Thing

def load_sim(uuid):
    return Thing.load_sim(uuid)

class BaseSim(object):

    @classmethod
    def create_sim(cls):
        return Thing.create_sim(cls)

    def save(self):
        return Thing.save_sim(self)

    def __init__(self, uuid):
        self.uuid = uuid

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        return self.__dict__.copy()

class Robot(BaseSim):

    pass
