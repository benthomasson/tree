
from leaf.models import Robot

from django.contrib import admin


class RobotAdmin(admin.ModelAdmin):
    list_display = ('uuid',)
admin.site.register(Robot, RobotAdmin)
