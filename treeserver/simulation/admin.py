

from simulation.models import Thing, Data, Task

from django.contrib import admin


class ThingAdmin(admin.ModelAdmin):
    list_display = ('uuid',
                    'sim_class')
admin.site.register(Thing, ThingAdmin)


class DataAdmin(admin.ModelAdmin):
    list_display = ('thing',
                    'name',
                    'value')
admin.site.register(Data, DataAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('thing',
                    'name',
                    'status',
                    'result')
admin.site.register(Task, TaskAdmin)
