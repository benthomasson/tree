

from simulation.models import Thing
from common.fn import class_name

def load_sim(uuid):
    return Thing.load_sim(uuid)

class BaseSim(object):

    @classmethod
    def create_sim(cls):
        return Thing.create_sim(cls)

    @classmethod
    def all(cls):
        return Thing.objects.filter(sim_class=class_name(cls))

    @classmethod
    def get(cls, uuid):
        return Thing.load_sim(uuid=uuid)

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
