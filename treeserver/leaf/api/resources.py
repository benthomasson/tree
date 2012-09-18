from tastypie.resources import ModelResource, ALL
from tastypie.authorization import Authorization
from tastypie import fields
from leaf.models import Robot, Configuration
from django.contrib.auth.models import User

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization


class RobotResource(ModelResource):

    class Meta:
        queryset = Robot.objects.all()
        allowed_methods = ['get']
        authentication = BasicAuthentication(realm="")
        authorization = DjangoAuthorization()

class ConfigurationResource(ModelResource):

    robot = fields.ForeignKey(RobotResource, 'robot')

    class Meta:
        queryset = Configuration.objects.all()
        allowed_methods = ['get', 'post']
        authentication = BasicAuthentication(realm="")
        authorization = DjangoAuthorization()
        filtering = {
            "robot": ('exact',),
        }
