from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.


from common.fields import UUIDField, JSONValueField

class Thing(models.Model):

    uuid = UUIDField(primary_key=True)

    def __str__(self):
        return self.uuid

    class Meta:
       verbose_name_plural = "Thingies"

class Data(models.Model):

    thing = models.ForeignKey(Thing)
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
        for name, value in thing.__getstate__.iteritems():
            cls.set_attribute(t, name, value)

    @classmethod
    def load_state(cls, uuid, o):
        d = dict()
        t = Thing.objects.get(uuid=uuid)
        for datum in cls.filter(thing=t):
            d[datum.name] = datum.value
        o.__setstate__(d)


