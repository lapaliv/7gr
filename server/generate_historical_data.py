import random

from climate.models import Device, HistoricalData
from climate.container import Container
from climate.enums import FanSpeed, DeviceType, ConditioningMode, HumidityMode, DehumidificationMode, DevicePower

sector_repository = Container.sector_repository()
device_repository = Container.device_repository()

sectors_offset = 0
sectors_limit = 100

fan_speeds = list(FanSpeed.__members__.keys())
conditioning_modes = list(ConditioningMode.__members__.keys())
humidity_modes = list(HumidityMode.__members__.keys())
dehumidification_modes = list(DehumidificationMode.__members__.keys())

while True:
    sectors = sector_repository.get_all(sectors_offset, sectors_limit)

    for sector in sectors:
        devices = device_repository.get_for_sector(sector)

        for device in devices:
            mode = None

            if device.type == DeviceType.CONDITIONER.value:
                mode = conditioning_modes[random.randint(0, len(conditioning_modes) - 1)]
            elif device.type == DeviceType.HUMIDIFIER.value:
                mode = humidity_modes[random.randint(0, len(humidity_modes) - 1)]
            elif device.type == DeviceType.DEHUMIDIFIER.value:
                mode = dehumidification_modes[random.randint(0, len(dehumidification_modes) - 1)]

            power = DevicePower.ON

            if random.randint(0, 100) == 0:
                power = DevicePower.OFF

            HistoricalData.objects.create(
                device = device,
                density = random.uniform(0, 100),
                temperature = random.uniform(18, 30),
                humidity = random.uniform(20, 80),
                fan_speed = fan_speeds[random.randint(0, len(fan_speeds) - 1)],
                mode = mode,
                power = power
            )

    if len(sectors) < sectors_limit:
        break
