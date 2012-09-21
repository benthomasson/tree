

from simulation.models import Thing, Data

from django.contrib import admin


class ThingAdmin(admin.ModelAdmin):
    list_display = ('uuid',)
admin.site.register(Thing, ThingAdmin)

class DataAdmin(admin.ModelAdmin):
    list_display = ('thing',
                    'name',
                    'value')
admin.site.register(Data, DataAdmin)
