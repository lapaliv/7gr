from django.core.management.base import BaseCommand
import statistics

from climate.container import Container
from climate.enums import Season
from climate.enums import DeviceType, DevicePower
from climate.repositories import (
    SectorRepository,
    DeviceRepository,
    UseCaseRepository,
    SeasonRepository
)


class Command(BaseCommand):
    DEFAULT_DESTINY = 50.0

    def __init__(self):
        super().__init__()

        self.sector_repository = Container.sector_repository()
        self.device_repository = Container.device_repository()
        self.use_case_repository = Container.use_case_repository()
        self.season_repository = Container.season_repository()

        self.conditioner_device_manager = Container.conditioner_device_manager()
        self.temperature_sensor_device_manager = Container.temperature_sensor_device_manager()
        self.humidity_sensor_device_manager = Container.humidity_sensor_device_manager()
        self.humidifier_device_manager = Container.humidifier_device_manager()
        self.dehumidifier_device_manager = Container.dehumidifier_device_manager()

        self.get_average_destiny_from_cameras_feature = Container.get_average_destiny_from_cameras_feature()

    def handle(self, *args, **kwargs):
        sectors = self.sector_repository.get_all()
        season = self.season_repository.get_current_season()

        for sector in sectors:
            devices = self.device_repository.get_for_sector(sector)
            devices_grouped_by_type = {}

            for device in devices:
                if device.type not in devices_grouped_by_type:
                    devices_grouped_by_type[device.type] = []

                devices_grouped_by_type[device.type].append(device)

            cameras = devices_grouped_by_type[DeviceType.CAMERA.value] if DeviceType.CAMERA.value in devices_grouped_by_type else []

            destiny = None
            if cameras:
                destiny = self.get_average_destiny_from_cameras_feature.handle(cameras)

            if destiny is None:
                destiny = self.DEFAULT_DESTINY


            self._manage_temperature(devices_grouped_by_type, season, destiny)
            self._manage_humidity(devices_grouped_by_type, season)

    def _manage_temperature(self, devices_grouped_by_type, season: Season, destiny: float):
        temperature_sensors = devices_grouped_by_type[DeviceType.TEMPERATURE_SENSOR.value] if DeviceType.TEMPERATURE_SENSOR.value in devices_grouped_by_type else []
        conditioners = devices_grouped_by_type[DeviceType.CONDITIONER.value] if DeviceType.CONDITIONER.value in devices_grouped_by_type else []

        if not conditioners:
            return

        temperature_values = []

        for temperature_sensor in temperature_sensors:
            driver = self.temperature_sensor_device_manager.get_driver(temperature_sensor)
            temperature = driver.get_temperature()
            temperature_values.append(temperature)

        for conditioner in conditioners:
            driver = self.conditioner_device_manager.get_driver(conditioner)
            temperature = driver.get_temperature()
            temperature_values.append(temperature)

        if not temperature_values:
            return

        actual = statistics.mean(temperature_values) if temperature_values else 0.0
        (min_target, max_target) = self.season_repository.get_temperature_span(season)
        target = (min_target + max_target) / 2
        use_cases = self.use_case_repository.get_by_temperature(actual, min_target, max_target, destiny)

        for use_case in use_cases:
            (fan_speed, mode, device_power) = use_case

            for conditioner in conditioners:
                if not conditioner.is_automatic:
                    continue

                driver = self.conditioner_device_manager.get_driver(conditioner)
                driver.set_power(device_power)

                if device_power == DevicePower.ON:
                    driver.set_temperature(target)
                    driver.set_fan_speed(fan_speed)
                    driver.set_mode(mode)

                    conditioner.power = DevicePower.ON.value
                    conditioner.target_temperature = target
                    conditioner.target_fan_speed = fan_speed.value
                    conditioner.target_mode = mode.value
                else:
                    conditioner.power = DevicePower.OFF.value
                    conditioner.target_temperature = None
                    conditioner.target_fan_speed = None
                    conditioner.target_mode = None

                conditioner.save()

    def _manage_humidity(self, devices_grouped_by_type, season: Season):
        humidity_sensors = devices_grouped_by_type[DeviceType.HUMIDITY_SENSOR.value] if DeviceType.HUMIDITY_SENSOR.value in devices_grouped_by_type else []
        humidifiers = devices_grouped_by_type[DeviceType.HUMIDIFIER.value] if DeviceType.HUMIDIFIER.value in devices_grouped_by_type else []
        dehumidifiers = devices_grouped_by_type[DeviceType.DEHUMIDIFIER.value] if DeviceType.DEHUMIDIFIER.value in devices_grouped_by_type else []

        humidity_values = []

        for humidity_sensor in humidity_sensors:
            driver = self.humidity_sensor_device_manager.get_driver(humidity_sensor)
            humidity = driver.get_humidity()
            humidity_values.append(humidity)

        for humidifier in humidifiers:
            driver = self.humidifier_device_manager.get_driver(humidifier)
            humidity = driver.get_humidity()
            humidity_values.append(humidity)

        for dehumidifier in dehumidifiers:
            driver = self.dehumidifier_device_manager.get_driver(dehumidifier)
            humidity = driver.get_humidity()
            humidity_values.append(humidity)

        actual = statistics.mean(humidity_values) if humidity_values else 0.0
        (min_target, max_target) = self.season_repository.get_humidity_span(season)
        use_cases = self.use_case_repository.get_by_humidity(actual, min_target, max_target)
        target = (min_target + max_target) / 2

        for use_case in use_cases:
            (device_type, fan_speed, mode, device_power) = use_case

            if device_type == DeviceType.HUMIDIFIER:
                for humidifier in humidifiers:
                    if not humidifier.is_automatic:
                        continue

                    driver = self.humidifier_device_manager.get_driver(humidifier)
                    driver.set_power(device_power)

                    if device_power == DevicePower.ON:
                        driver.set_humidity(target)
                        driver.set_fan_speed(fan_speed)
                        driver.set_mode(mode)
                        humidifier.power = DevicePower.ON.value
                        humidifier.target_temperature = target
                        humidifier.target_fan_speed = fan_speed.value
                        humidifier.target_mode = mode.value
                    else:
                        humidifier.power = DevicePower.OFF.value
                        humidifier.target_temperature = None
                        humidifier.target_fan_speed = None
                        humidifier.target_mode = None

                    humidifier.save()
            elif device_type == DeviceType.DEHUMIDIFIER:
                for dehumidifier in dehumidifiers:
                    if not dehumidifier.is_automatic:
                        continue

                    driver = self.dehumidifier_device_manager.get_driver(dehumidifier)
                    driver.set_power(device_power)

                    if device_power == DevicePower.ON:
                        driver.set_humidity(target)
                        driver.set_fan_speed(fan_speed)
                        driver.set_mode(mode)
                        dehumidifier.power = DevicePower.ON.value
                        dehumidifier.target_temperature = target
                        dehumidifier.target_fan_speed = fan_speed.value
                        dehumidifier.target_mode = mode.value
                    else:
                        dehumidifier.power = DevicePower.OFF.value
                        dehumidifier.target_temperature = None
                        dehumidifier.target_fan_speed = None
                        dehumidifier.target_mode = None

                    dehumidifier.save()
            else:
                raise ValueError(f"Unknown device type: {device_type.value}")

