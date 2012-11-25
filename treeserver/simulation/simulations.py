

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
        return map(lambda x: Thing.load_sim(uuid=x.uuid), Thing.objects.filter(sim_class=class_name(cls)))

    @classmethod
    def filter(cls,**kwargs):
        return map(lambda x: Thing.load_sim(uuid=x.uuid), Thing.objects.filter(**kwargs))

    @classmethod
    def get(cls, uuid):
        return Thing.load_sim(uuid=uuid)

    def save(self):
        return Thing.save_sim(self)

    def __init__(self, uuid=None):
        self.uuid = uuid

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        return self.__dict__.copy()

    def __str__(self):
        return "{0} {1} {2}".format(class_name(self.__class__), self.uuid, self.__dict__)

class Robot(BaseSim):

    def task_hello(self, task):
        task.status = 'COMPLETED'
        task.save()
        return "Hello"

