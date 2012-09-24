
from leaf.models import Robot, Ability

from django.contrib import admin


class RobotAdmin(admin.ModelAdmin):
    list_display = ('uuid',)
admin.site.register(Robot, RobotAdmin)

class AbilityAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'function',)
admin.site.register(Ability, AbilityAdmin)
