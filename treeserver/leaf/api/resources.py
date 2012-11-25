from tastypie.resources import ModelResource, ALL, Resource
from tastypie.authorization import Authorization
from tastypie import fields, http
from tastypie.bundle import Bundle
from leaf.models import Robot, Ability
from simulation.simulations import Robot as Robot2
from simulation.models import Thing, Task
from django.contrib.auth.models import User
from django.http import HttpResponse
from tastypie.exceptions import ImmediateHttpResponse

from tastypie.authentication import BasicAuthentication
import functools


class XHMOMixin(object):
    """
    Use to supply a Tastypie resource with support for X-HTTP-Method-Override
    headers, e.g.:

    `class HomeResource(XHMOMixin, ModelResource):`
    """

    def method_check(self, request, allowed=None):
        """
        Ensures that the HTTP method used on the request is allowed to be
        handled by the resource.

        Patched with X-HTTP-Method-Override:
        https://github.com/toastdriven/django-tastypie/pull/351

        Takes an ``allowed`` parameter, which should be a list of lowercase
        HTTP methods to check against. Usually, this looks like::

            # The most generic lookup.
            self.method_check(request, self._meta.allowed_methods)

            # A lookup against what's allowed for list-type methods.
            self.method_check(request, self._meta.list_allowed_methods)

            # A useful check when creating a new endpoint that only handles
            # GET.
            self.method_check(request, ['get'])
        """
        if allowed is None:
            allowed = []

        # Normally we'll just use request.method to determine the request
        # method. However, since some bad clients can't support all HTTP
        # methods, we allow overloading POST requests with a
        # X-HTTP-Method-Override header. This allows POST requests to
        # masquerade as different methods.
        request_method = request.method.lower()
        if request_method == 'post' and 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
            request_method = request.META['HTTP_X_HTTP_METHOD_OVERRIDE'].lower()

        allows = ','.join(map(str.upper, allowed))

        if request_method == "options":
            response = HttpResponse(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        if not request_method in allowed:
            response = http.HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        return request_method


class ObjectAuthorization(Authorization):

    def __init__(self, auth_key, object_key):
        self.auth_key = auth_key
        self.object_key = object_key

    def apply_limits(self, request, object_list):
        return filter(functools.partial(self.test_auth_key, request), object_list)

    def test_auth_key(self, request, obj):
        if not hasattr(obj, self.object_key):
            return True
        else:
            return self.get_auth_key(request) == getattr(obj, self.object_key)

    def get_auth_key(self, request):
        return request.META.get(self.auth_key)

    def is_authorized(self, request, obj):
        if obj is None:
            return True
        return self.test_auth_key(request, obj)


class RobotResource(XHMOMixin, ModelResource):

    class Meta:
        queryset = Robot.objects.all()
        allowed_methods = ['post', 'get', 'put']
        authentication = BasicAuthentication(realm="")
        authorization = Authorization()
        #authorization = ObjectAuthorization('HTTP_AUTHORIZATION_KEY', 'authorization')


class AbilityResource(ModelResource):

    class Meta:
        queryset = Ability.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        excludes = ['function', 'id']
        authentication = BasicAuthentication(realm="")
        authorization = Authorization()


class ThingResource(Resource):

    def rollback(self, bundles):
        pass

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.uuid
        else:
            kwargs['pk'] = bundle_or_obj.uuid
        return kwargs

    def obj_get_list(self, request=None, **kwargs):
        auth = self._meta.authorization
        objects = auth.apply_limits(request, self._meta.object_class.filter(authorization=auth.get_auth_key(request)))
        return objects

    def obj_get(self, request=None, **kwargs):
        o = self._meta.object_class.get(uuid=kwargs['pk'])
        self.is_authorized(request, o)
        return o

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = Thing.create_sim(self._meta.object_class)
        self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        bundle.obj = Thing.load_sim(bundle.data['uuid'])
        self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle

    #def dehydrate_authorization(self, bundle):
    #    return bundle.data['authorization']


class RobotResource2(XHMOMixin, ThingResource):

    uuid = fields.CharField(attribute='uuid', readonly=True, unique=True, help_text="uuid")
    authorization = fields.CharField(attribute='authorization', readonly=False, help_text="authorization", blank=True, null=True)
    alias = fields.CharField(attribute='alias', help_text="alias", blank=True, null=True)

    class Meta:
        resource_name = 'robot2'
        object_class = Robot2
        allowed_methods = ['post', 'get', 'put']
        authentication = BasicAuthentication(realm="")
        authorization = ObjectAuthorization('HTTP_AUTHORIZATION_KEY', 'authorization')

class TaskResource(XHMOMixin, Resource):

    task = fields.CharField(attribute='uuid', readonly=True, unique=True, help_text="uuid")
    uuid = fields.CharField(attribute='uuid', help_text="uuid")
    name = fields.CharField(attribute='name', help_text="name")
    authorization = fields.CharField(attribute='authorization', readonly=False, help_text="authorization", blank=True, null=True)
    status = fields.CharField(attribute='status', help_text="status", readonly=True)
    result = fields.CharField(attribute='result', help_text="result", readonly=True)

    class Meta:
        resource_name = 'task'
        allowed_methods = ['post', 'get', 'put']
        authentication = BasicAuthentication(realm="")
        authorization = ObjectAuthorization('HTTP_AUTHORIZATION_KEY', 'authorization')

    def rollback(self, bundles):
        pass

    def detail_uri_kwargs(self, bundle_or_obj):
        print 'detail_uri_kwargs'
        print bundle_or_obj
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.pk
        else:
            kwargs['pk'] = bundle_or_obj.task
        return kwargs

    def obj_get_list(self, request=None, **kwargs):
        auth = self._meta.authorization
        objects = auth.apply_limits(request, Task.filter(authorization=auth.get_auth_key(request)))
        return objects

    def obj_get(self, request=None, **kwargs):
        print 'obj_get'
        print request
        print kwargs
        o = Task.objects.get(id=kwargs['pk'])
        self.is_authorized(request, o)
        print o
        return o

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = Task()
        self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        o = Task.objects.get(pk=kwargs['pk'])
        self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle
