from django.db import models

from . import enums

class Sector(models.Model):
    name = models.CharField(max_length=50)

# class DeviceQuerySet(models.QuerySet):
#     def where_type_is_conditioner(self):
#         return self.filter(type=DeviceType.CONDITIONER)
#
# class DeviceManager(models.Manager):
#     def get_queryset(self):
#         return DeviceQuerySet(self.model, using=self._db)
#
#     def conditioners(self):
#         return self.get_queryset().where_type_is_conditioner()

class Device(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    host = models.CharField(max_length=15)
    port = models.IntegerField()
    is_automatic = models.BooleanField(default=True)
    target_temperature = models.FloatField(null = True, default=None)
    target_humidity = models.FloatField(null = True, default=None)
    target_fan_speed = models.CharField(null = True, max_length=10)
    target_mode = models.CharField(null = True, max_length=10)
    power = models.CharField(null = False, max_length=3, default = 'on')
