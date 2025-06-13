from django.db import models
from django.core.exceptions import ValidationError
from climate.enums import (
    DevicePower,
    ConditioningMode,
    HumidityMode,
    DehumidificationMode,
    FanSpeed,
    DeviceType
)

class Sector(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

class Device(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    type = models.CharField(max_length = 20, choices = DeviceType.choices())
    host = models.CharField(max_length = 15)
    port = models.IntegerField()
    is_automatic = models.BooleanField(default=True)
    current_temperature = models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)
    target_temperature = models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)
    current_humidity = models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)
    target_humidity = models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)
    current_fan_speed = models.CharField(
        null = True,
        max_length = 10,
        choices = FanSpeed.choices(),
    )
    target_fan_speed = models.CharField(
        null = True,
        max_length = 10,
        choices = FanSpeed.choices(),
    )
    current_mode = models.CharField(
        null = True,
        max_length = 10,
        choices = list(
            dict.fromkeys(
                [*ConditioningMode.choices(), *HumidityMode.choices(), *DehumidificationMode.choices()]
            )
        )
    )
    target_mode = models.CharField(
        null = True,
        max_length = 10,
        choices = list(
            dict.fromkeys(
                [*ConditioningMode.choices(), *HumidityMode.choices(), *DehumidificationMode.choices()]
            )
        )
    )
    power = models.CharField(
        null = False,
        max_length = 3,
        default = DevicePower.ON.value,
        choices = DevicePower.choices(),
    )
    error = models.TextField(null = True, default = None)

    def clean(self):
        conflict_qs = Device.objects.exclude(pk=self.pk).filter(host=self.host, port=self.port)
        if conflict_qs.exists():
            raise ValidationError({'host': f'Device with host {self.host} and port {self.port} already exists.'})

    def __str__(self):
        return f'{self.host}:{self.port} ({self.type})'
