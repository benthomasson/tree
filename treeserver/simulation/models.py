from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

from common.fields import UUIDField, JSONValueField
from common.fn import load_fn, class_name

import random
import hashlib


def generate_authorization():
    return hashlib.sha256(str(random.getrandbits(256))).hexdigest()


class Thing(models.Model):

    uuid = UUIDField(primary_key=True)
    sim_class = models.CharField(max_length=255, db_index=True)
    authorization = models.CharField(max_length=64, default=generate_authorization, blank=True)

    def __str__(self):
        return self.uuid

    class Meta:
        verbose_name_plural = "Thingies"

    @classmethod
    def create_thing(cls, sim_class):
        thing = cls(sim_class=class_name(sim_class))
        thing.save()
        return thing

    @classmethod
    def create_sim(cls, sim_class):
        thing = cls.create_thing(sim_class)
        return sim_class(thing.uuid)

    @classmethod
    def load_sim(cls, uuid):
        thing = cls.objects.get(uuid=uuid)
        return thing.load_my_sim()

    def load_my_sim(self):
        sim_class = load_fn(self.sim_class)
        sim = sim_class.__new__(sim_class)
        sim.authorization = self.authorization
        Data.load_state(self, sim)
        return sim

    @classmethod
    def save_sim(cls, sim):
        thing = cls.objects.get(uuid=sim.uuid)
        if hasattr(sim, 'authorization') and sim.authorization and sim.authorization != thing.authorization:
            thing.authorization = sim.authorization
            thing.save()
        Data.save_state(thing, sim)


class Data(models.Model):

    thing = models.ForeignKey(Thing, db_index=True)
    name = models.CharField(max_length=255)
    value = JSONValueField()

    class Meta:
        verbose_name_plural = "Data"

    @classmethod
    def get_attribute(cls, thing, name):
        return cls.objects.get(thing=thing, name=name).value

    @classmethod
    def set_attribute(cls, thing, name, value):
        try:
            datum = cls.objects.get(thing=thing, name=name)
            datum.value = value
            datum.save()
        except ObjectDoesNotExist:
            datum = cls(thing=thing, name=name, value=value)
            datum.save()

    @classmethod
    def save_state(cls, thing, o):
        state = o.__getstate__()
        for var in ['uuid', 'authorization']:
            if var in state:
                del state[var]
        for name, value in state.iteritems():
            cls.set_attribute(thing, name, value)

    @classmethod
    def load_state(cls, thing, o):
        d = dict()
        for datum in cls.objects.filter(thing=thing):
            d[datum.name] = datum.value
        o.__setstate__(d)
        o.uuid = thing.uuid


class Task(models.Model):

    thing = models.ForeignKey(Thing, db_index=True)
    name = models.CharField(max_length=255)
    kwargs = JSONValueField(default=dict())
    authorization = models.CharField(max_length=64, default=generate_authorization, blank=True)
    status = models.CharField(max_length=20, default='REQUESTED')
    result = JSONValueField(default=None)

    def call_sim_method(self):
        sim = self.thing.load_my_sim()
        method_name = 'task_{0}'.format(self.name)
        assert hasattr(sim, method_name)
        fn = getattr(sim, method_name)
        self.result = fn(task=self, **self.kwargs)
        self.save()

    def __str__(self):
        return "{1}.{2} #{0}".format(self.id, self.thing.uuid, self.name)
