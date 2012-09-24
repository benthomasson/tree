from tastypie.resources import ModelResource, ALL
from tastypie.authorization import Authorization
from tastypie import fields
from leaf.models import Robot, Ability
from django.contrib.auth.models import User

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
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


class RobotResource(XHMOMixin, ModelResource):

    class Meta:
        queryset = Robot.objects.all()
        allowed_methods = ['post', 'get', 'put' ]
        authentication = BasicAuthentication(realm="")
        authorization = DjangoAuthorization()
        #authorization = ObjectAuthorization('HTTP_AUTHORIZATION_KEY', 'authorization')

class AbilityResource(ModelResource):

    class Meta:
        queryset = Ability.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        excludes = ['function', 'id']
        authentication = BasicAuthentication(realm="")
        authorization = DjangoAuthorization()
