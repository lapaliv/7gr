from django.core.management.base import BaseCommand
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware

from climate.models import Device, HistoricalData
from climate.container import Container
from climate.enums import FanSpeed, DeviceType, ConditioningMode, HumidityMode, DehumidificationMode, DevicePower

class Command(BaseCommand):
    def __init__(self):
        super().__init__()

        self.sector_service = Container.sector_service()
        self.device_repository = Container.device_repository()

    def handle(self, *args, **kwargs):
        sector_repository = Container.sector_repository()

        sectors_offset = 0
        sectors_limit = 100

        fan_speeds = list(FanSpeed.__members__.keys())
        conditioning_modes = list(ConditioningMode.__members__.keys())
        humidity_modes = list(HumidityMode.__members__.keys())
        dehumidification_modes = list(DehumidificationMode.__members__.keys())

        now = datetime.now()

        while True:
            sectors = sector_repository.get_all(sectors_offset, sectors_limit)

            for sector in sectors:
                devices = self.device_repository.get_for_sector(sector)
                current_time = (datetime.now() - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
                temperature = 24

                while current_time < now:
                    for device in devices:
                        timestamp = make_aware(current_time)

                        if not HistoricalData.objects.filter(device=device, created_at=timestamp).exists():
                            density = self.get_density(device, current_time)
                            temperature = self.get_temperature(device)
                            humidity = self.get_humidity(device)
                            fan_speed = self.get_fan_speed(device)

                            if density == None and temperature == None and humidity == None and fan_speed == None:
                                continue

                            HistoricalData.objects.create(
                                device=device,
                                density=density,
                                temperature=temperature,
                                humidity=humidity,
                                fan_speed=fan_speed,
                                mode=None,
                                power=self.get_power(device),
                                created_at=timezone.make_aware(current_time)
                            )

                    print(sector.id, current_time)
                    current_time += timedelta(minutes=1)

            if len(sectors) < sectors_limit:
                break

    def get_density(self, device, minute: datetime) -> int | None:
        if device.type != DeviceType.CAMERA.value:
            return None

        time = minute.time()

        if time < datetime.strptime("08:45", "%H:%M").time():
            return 0
        elif time >= datetime.strptime("23:00", "%H:%M").time():
            return 0
        elif time < datetime.strptime("09:00", "%H:%M").time():
            return random.randint(0, 10)
        elif time < datetime.strptime("21:00", "%H:%M").time():
            if random.random() < 0.5:
                return random.randint(0, 10)
            else:
                return random.randint(0, 30)
        elif time < datetime.strptime("21:45", "%H:%M").time():
            return random.randint(0, 10)
        elif time < datetime.strptime("22:00", "%H:%M").time():
            return random.randint(0, 5)
        elif time < datetime.strptime("23:00", "%H:%M").time():
            if random.random() < 0.9:
                return 0
            else:
                return random.randint(0, 2)

    def get_temperature(self, device) -> int | None:
        if device.type != DeviceType.CONDITIONER.value and device.type != DeviceType.TEMPERATURE_SENSOR.value:
            return None

        if random.random() < 0.5:
            return 24

        return random.randint(20, 26)

    def get_humidity(self, device) -> int | None:
        if device.type != DeviceType.HUMIDIFIER.value and device.type != DeviceType.HUMIDITY_SENSOR.value:
            return None

        if random.random() < 0.5:
            return 50

        return random.randint(30, 70)

    def get_fan_speed(self, device):
        if device.type != DeviceType.FAN.value:
            return None

        if random.random() < 0.5:
            return FanSpeed.MEDIUM.value

        if random.random() < 0.5:
            return FanSpeed.LOW.value

        return FanSpeed.HIGH.value


    def get_power(self, device):
        if device.type != DeviceType.DEHUMIDIFIER.value:
            return DevicePower.OFF

        return DevicePower.ON
