from django.db import models

# Create your models here.

from common.fields import UUIDField, JSONDictField

import random
import hashlib

def generate_authorization():
    return hashlib.sha256( str(random.getrandbits(256)) ).hexdigest()

class Robot(models.Model):

    uuid = UUIDField(primary_key=True)
    alias = models.CharField(max_length=80, blank=True, default="")
    authorization = models.CharField(max_length=64, default=generate_authorization, blank=True)

    def __str__(self):
        return self.uuid
