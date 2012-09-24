from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.


from common.fields import UUIDField, JSONValueField
from common.fn import load_fn, class_name

class Thing(models.Model):

    uuid = UUIDField(primary_key=True)
    sim_class = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.uuid

    class Meta:
       verbose_name_plural = "Thingies"

    @classmethod
    def create_sim(cls, sim_class):
        thing = cls(sim_class=class_name(sim_class))
        thing.save()
        return sim_class(thing.uuid)

    @classmethod
    def load_sim(cls, uuid):
        thing = cls.objects.get(uuid=uuid)
        sim_class = load_fn(thing.sim_class)
        sim = sim_class.__new__(sim_class)
        Data.load_state(thing.uuid, sim)
        return sim

    @classmethod
    def save_sim(cls, sim):
        thing = cls.objects.get(uuid=sim.uuid)
        Data.save_state(thing, sim)

class Data(models.Model):

    thing = models.ForeignKey(Thing, db_index=True)
    name = models.CharField(max_length=255)
    value = JSONValueField()

    class Meta:
       verbose_name_plural = "Data"

    @classmethod
    def get_attribute(cls, thing, name):
        return cls.objects.get(thing=thing,name=name).value

    @classmethod
    def set_attribute(cls, thing, name, value):
        try:
            datum = cls.objects.get(thing=thing,name=name)
            datum.value = value
            datum.save()
        except ObjectDoesNotExist:
            datum = cls(thing=thing,name=name,value=value)
            datum.save()

    @classmethod
    def save_state(cls, uuid, o):
        t = Thing.objects.get(uuid=uuid)
        state = o.__getstate__()
        if 'uuid'in state:
            del state['uuid']
        for name, value in state.iteritems():
            cls.set_attribute(t, name, value)

    @classmethod
    def load_state(cls, uuid, o):
        d = dict()
        t = Thing.objects.get(uuid=uuid)
        for datum in cls.objects.filter(thing=t):
            d[datum.name] = datum.value
        o.__setstate__(d)
        o.uuid = uuid


