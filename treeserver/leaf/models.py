from django.db import models

# Create your models here.

from common.fields import UUIDField


class Robot(models.Model):

    uuid = UUIDField(primary_key=True)


class Configuration(models.Model):

    robot = models.ForeignKey(Robot)
    config_line = models.CharField(max_length=80)



