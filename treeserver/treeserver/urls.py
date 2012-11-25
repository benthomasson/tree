from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from leaf.api.resources import RobotResource, AbilityResource, RobotResource2, TaskResource

leaf_v1_api = Api(api_name='v1')
leaf_v1_api.register(RobotResource())
leaf_v1_api.register(AbilityResource())
leaf_v1_api.register(RobotResource2())
leaf_v1_api.register(TaskResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'treeserver.views.home', name='home'),
    # url(r'^treeserver/', include('treeserver.foo.urls')),

    #Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^leaf_api/', include(leaf_v1_api.urls)),
)
