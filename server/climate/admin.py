from django.contrib import admin
from climate.models import Sector, Device
from climate.enums import DeviceType, DevicePower

admin.site.register(Sector)

class DeviceAdmin(admin.ModelAdmin):
    exclude = ['current_density', 'current_temperature', 'current_humidity', 'current_fan_speed', 'current_mode', 'error']

    def get_readonly_fields(self, request, obj=None):
        readonly = []

        if (
            obj is not None and
            obj.power == DevicePower.OFF.value
        ):
            readonly.append('is_automatic')
            readonly.append('target_temperature')
            readonly.append('target_humidity')
            readonly.append('target_fan_speed')
            readonly.append('target_mode')

        if (
            obj is None or
            obj.is_automatic or
            obj.type == DeviceType.TEMPERATURE_SENSOR.value or
            obj.type == DeviceType.HUMIDITY_SENSOR.value or
            obj.type == DeviceType.CAMERA.value
        ):
            readonly.append('target_temperature')
            readonly.append('target_humidity')
            readonly.append('target_fan_speed')
            readonly.append('target_mode')

        elif (
            obj is not None and
            obj.is_automatic == False and
            obj.type == DeviceType.CONDITIONER.value
        ):
            readonly.append('target_humidity')

        elif (
            obj is not None and
            obj.is_automatic == False and
            (obj.type == DeviceType.HUMIDIFIER.value or obj.type == DeviceType.DEHUMIDIFIER.value)
        ):
            readonly.append('target_temperature')

        elif (
            obj is not None and
            obj.is_automatic == False and
            obj.type == DeviceType.FAN.value
        ):
            readonly.append('target_temperature')
            readonly.append('target_humidity')
            readonly.append('target_mode')

        if obj != None and (obj.type == DeviceType.TEMPERATURE_SENSOR.value or obj.type == DeviceType.HUMIDITY_SENSOR.value):
            readonly.append('is_automatic')

        readonly = list(set(readonly))

        return readonly

admin.site.register(Device, DeviceAdmin)
