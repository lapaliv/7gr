from django.contrib import admin
from climate.models import Sector, Device
from climate.enums import DeviceType

admin.site.register(Sector)

class DeviceAdmin(admin.ModelAdmin):
    exclude = ['current_temperature', 'current_humidity', 'current_fan_speed', 'current_mode', 'error']

    def get_readonly_fields(self, request, obj=None):
        readonly = []

        if obj is None or obj.is_automatic or obj.type == DeviceType.TEMPERATURE_SENSOR.value or obj.type == DeviceType.HUMIDITY_SENSOR.value:
            readonly.append('target_temperature')
            readonly.append('target_humidity')
            readonly.append('target_fan_speed')
            readonly.append('target_mode')

        if obj is None or obj.is_automatic:
            readonly.append('power')

        return readonly

admin.site.register(Device, DeviceAdmin)
