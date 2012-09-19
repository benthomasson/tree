from tastypie.resources import ModelResource, ALL
from tastypie.authorization import Authorization
from tastypie import fields
from leaf.models import Robot, Configuration
from django.contrib.auth.models import User

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
import functools


class ObjectAuthorization(DjangoAuthorization):

    def __init__(self, auth_key, object_key):
        self.auth_key = auth_key
        self.object_key = object_key

    def apply_limits(self, request, object_list):
        print request.META
        print object_list
        return filter(functools.partial(self.test_auth_key, request), object_list)

    def test_auth_key(self, request, obj):
        if not hasattr(obj, self.object_key):
            return True
        else:
            return request.META.get(self.auth_key) == getattr(obj, self.object_key)


class RobotResource(ModelResource):

    class Meta:
        queryset = Robot.objects.all()
        allowed_methods = ['get']
        authentication = BasicAuthentication(realm="")
        authorization = ObjectAuthorization('HTTP_AUTHORIZATION_KEY', 'authorization')


class ConfigurationResource(ModelResource):

    robot = fields.ForeignKey(RobotResource, 'robot')

    class Meta:
        queryset = Configuration.objects.all()
        allowed_methods = ['get', 'post']
        authentication = BasicAuthentication(realm="")
        authorization = DjangoAuthorization()
        filtering = {
            "robot": ('exact', ),
        }
