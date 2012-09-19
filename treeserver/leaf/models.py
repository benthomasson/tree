from django.db import models

# Create your models here.

from common.fields import UUIDField

import random
import hashlib

def generate_authorization():
    return hashlib.sha256( str(random.getrandbits(256)) ).hexdigest()

class Robot(models.Model):

    uuid = UUIDField(primary_key=True)
    authorization = models.CharField(max_length=64, default=generate_authorization, blank=True)

    def __str__(self):
        return self.uuid

class Configuration(models.Model):

    robot = models.ForeignKey(Robot)
    config_line = models.CharField(max_length=80)



