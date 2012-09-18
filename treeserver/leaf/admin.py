
from leaf.models import Robot, Configuration

from django.contrib import admin


class RobotAdmin(admin.ModelAdmin):
    list_display = ('uuid',)
admin.site.register(Robot, RobotAdmin)

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('robot',
                    'config_line',)
admin.site.register(Configuration, ConfigurationAdmin)
