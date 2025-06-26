from django.core.management.base import BaseCommand
import statistics
import math

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
        self.camera_device_manager = Container.camera_device_manager()
        self.fan_device_manager = Container.fan_device_manager()

        self.computer_vision = Container.computer_vision()

    def handle(self, *args, **kwargs):
        sectors_offset = 0
        sectors_limit = 100

        while True:
            sectors = self.sector_repository.get_all(sectors_offset, sectors_limit)
            season = self.season_repository.get_current_season()

            for sector in sectors:
                print("-" * 10, 'SECTOR:', sector.name, '-' * 10)
                devices = self.device_repository.get_for_sector(sector)
                devices_grouped_by_type = {}

                for device in devices:
                    if device.type not in devices_grouped_by_type:
                        devices_grouped_by_type[device.type] = []

                    devices_grouped_by_type[device.type].append(device)

                print("-" * 3, 'State', '-' * 3)

                density = self.__get_average_density(devices_grouped_by_type)
                print('Average density:', f'{density} pers/m²')

                current_temperature = self._get_current_temperature(devices_grouped_by_type)
                print('Average temperature:', 'None' if current_temperature is None else f'{current_temperature} °C')

                current_humidity = self._get_current_humidity(devices_grouped_by_type)
                print('Average humidity:', 'None' if current_humidity is None else f'{current_humidity}%')

                if current_temperature or current_humidity:
                    print("-" * 3, 'Updates', '-' * 3)

                self._manage_fan(devices_grouped_by_type, density)

                if current_temperature:
                    self._manage_temperature(devices_grouped_by_type, season, density, current_temperature)

                if current_humidity:
                    self._manage_humidity(devices_grouped_by_type, season, current_humidity)

            if len(sectors) < sectors_limit:
                break

    def __get_average_density(self, devices_grouped_by_type) -> float:
        cameras = devices_grouped_by_type[DeviceType.CAMERA.value] if DeviceType.CAMERA.value in devices_grouped_by_type else []
        values = []

        for camera in cameras:
            driver = self.camera_device_manager.get_driver(camera)
            photo = driver.get_photo()
            density = self.computer_vision.get_number_of_people(photo)

            camera.current_density = density
            camera.save()

            values.append(density)

        result = statistics.mean(values) if values else 50.0

        return math.floor(result * 100) / 100

    def _get_current_temperature(self, devices_grouped_by_type) -> float | None:
        temperature_sensors = devices_grouped_by_type[DeviceType.TEMPERATURE_SENSOR.value] if DeviceType.TEMPERATURE_SENSOR.value in devices_grouped_by_type else []
        conditioners = devices_grouped_by_type[DeviceType.CONDITIONER.value] if DeviceType.CONDITIONER.value in devices_grouped_by_type else []

        if not conditioners:
            return None

        temperature_values = []

        for temperature_sensor in temperature_sensors:
            driver = self.temperature_sensor_device_manager.get_driver(temperature_sensor)

            try:
                temperature = driver.get_temperature()
                temperature_values.append(temperature)

                temperature_sensor.current_temperature = temperature
                temperature_sensor.current_fan_speed = None
                temperature_sensor.current_mode = None
                temperature_sensor.error = None
            except Exception as e:
                temperature_sensor.error = str(e)
            finally:
                temperature_sensor.save()

        for conditioner in conditioners:
            driver = self.conditioner_device_manager.get_driver(conditioner)

            try:
                temperature = driver.get_temperature()
                temperature_values.append(temperature)

                conditioner.current_temperature = temperature
                conditioner.current_fan_speed = driver.get_fan_speed()
                conditioner.current_mode = driver.get_mode()
                conditioner.error = None
            except Exception as e:
                conditioner.error = str(e)
            finally:
                conditioner.save()

        if not temperature_values:
            return

        result = statistics.mean(temperature_values) if temperature_values else 0.0

        return math.floor(result * 100) / 100

    def _manage_temperature(self, devices_grouped_by_type, season: Season, density: float, current_temperature: float):
        temperature_sensors = devices_grouped_by_type[DeviceType.TEMPERATURE_SENSOR.value] if DeviceType.TEMPERATURE_SENSOR.value in devices_grouped_by_type else []
        conditioners = devices_grouped_by_type[DeviceType.CONDITIONER.value] if DeviceType.CONDITIONER.value in devices_grouped_by_type else []

        if not conditioners:
            return

        (min_target, max_target) = self.season_repository.get_temperature_span(season)
        target_temperature = (min_target + max_target) / 2
        use_cases = self.use_case_repository.get_conditioning_use_cases(current_temperature, min_target, max_target, density)

        for use_case in use_cases:
            (target_fan_speed, target_mode, target_device_power) = use_case

            for conditioner in conditioners:
                if not conditioner.is_automatic:
                    continue

                driver = self.conditioner_device_manager.get_driver(conditioner)

                try:
                    if driver.get_power() != target_device_power:
                        print(f'Conditioner #{conditioner.id} power:', DevicePower(driver.get_power()), '->', target_device_power.value)

                    driver.set_power(target_device_power)

                    if target_device_power == DevicePower.ON:
                        if driver.get_temperature() != target_temperature:
                            print(f'Conditioner #{conditioner.id} temperature:', driver.get_temperature(), '->', target_temperature)
                            driver.set_temperature(target_temperature)

                        if driver.get_fan_speed() != target_fan_speed:
                            print(f'Conditioner #{conditioner.id} fan speed:', driver.get_fan_speed(), '->', target_fan_speed.value)
                            driver.set_fan_speed(target_fan_speed)

                        if driver.get_mode() != target_mode:
                            print(f'Conditioner #{conditioner.id} mode:', driver.get_mode(), '->', target_mode.value)
                            driver.set_mode(target_mode)

                        conditioner.power = DevicePower.ON.value
                        conditioner.target_temperature = target_temperature
                        conditioner.target_fan_speed = target_fan_speed.value
                        conditioner.target_mode = target_mode.value
                    else:
                        conditioner.power = DevicePower.OFF.value
                        conditioner.target_temperature = None
                        conditioner.target_fan_speed = None
                        conditioner.target_mode = None
                    conditioner.error = None
                except Exception as e:
                    conditioner.error = str(e)
                finally:
                    conditioner.save()

    def _manage_fan(self, devices_grouped_by_type, density: float):
        fans = devices_grouped_by_type[DeviceType.FAN.value] if DeviceType.FAN.value in devices_grouped_by_type else []

        if not fans:
            return

        use_cases = self.use_case_repository.get_fan_use_case_by_destiny(density)

        for use_case in use_cases:
            (target_speed, target_device_power) = use_case

            for fan in fans:
                if not fan.is_automatic:
                    continue

                driver = self.fan_device_manager.get_driver(fan)

                try:
                    if driver.get_power() != target_device_power:
                        print(f'Fan #{fan.id} power:', DevicePower(driver.get_power()), '->', target_device_power.value)

                    driver.set_power(target_device_power)

                    if target_device_power == DevicePower.ON:
                        if driver.get_speed() != target_speed:
                            print(f'Fan #{fan.id} speed:', driver.get_speed(), '->', target_speed.value)
                            driver.set_speed(target_speed)

                        fan.power = DevicePower.ON.value
                        fan.current_fan_speed = driver.get_speed()
                        fan.target_fan_speed = target_speed.value
                    else:
                        fan.power = DevicePower.OFF.value
                        fan.current_fan_speed = None
                        fan.target_fan_speed = None
                    fan.error = None
                except Exception as e:
                    fan.error = str(e)
                finally:
                    fan.save()

    def _get_current_humidity(self, devices_grouped_by_type) -> float | None:
        humidity_sensors = devices_grouped_by_type[DeviceType.HUMIDITY_SENSOR.value] if DeviceType.HUMIDITY_SENSOR.value in devices_grouped_by_type else []
        humidifiers = devices_grouped_by_type[DeviceType.HUMIDIFIER.value] if DeviceType.HUMIDIFIER.value in devices_grouped_by_type else []
        dehumidifiers = devices_grouped_by_type[DeviceType.DEHUMIDIFIER.value] if DeviceType.DEHUMIDIFIER.value in devices_grouped_by_type else []

        humidity_values = []

        for humidity_sensor in humidity_sensors:
            driver = self.humidity_sensor_device_manager.get_driver(humidity_sensor)
            humidity = driver.get_humidity()
            humidity_values.append(humidity)

            humidity_sensor.current_humidity = humidity
            humidity_sensor.current_fan_speed = None
            humidity_sensor.current_mode = None
            humidity_sensor.save()

        for humidifier in humidifiers:
            driver = self.humidifier_device_manager.get_driver(humidifier)
            humidity = driver.get_humidity()
            humidity_values.append(humidity)

            humidifier.current_humidity = humidity
            humidifier.current_fan_speed = driver.get_fan_speed()
            humidifier.current_mode = driver.get_mode()
            humidifier.save()

        for dehumidifier in dehumidifiers:
            driver = self.dehumidifier_device_manager.get_driver(dehumidifier)
            humidity = driver.get_humidity()
            humidity_values.append(humidity)

            dehumidifier.current_humidity = humidity
            dehumidifier.current_fan_speed = driver.get_fan_speed()
            dehumidifier.current_mode = driver.get_mode()
            dehumidifier.save()

        result = statistics.mean(humidity_values) if humidity_values else None

        return None if result == None else (math.floor(result * 100) / 100)

    def _manage_humidity(self, devices_grouped_by_type, season: Season, current_humidity: float):
        humidifiers = devices_grouped_by_type[DeviceType.HUMIDIFIER.value] if DeviceType.HUMIDIFIER.value in devices_grouped_by_type else []
        dehumidifiers = devices_grouped_by_type[DeviceType.DEHUMIDIFIER.value] if DeviceType.DEHUMIDIFIER.value in devices_grouped_by_type else []

        (min_target, max_target) = self.season_repository.get_humidity_span(season)
        use_cases = self.use_case_repository.get_humidity_use_cases(current_humidity, min_target, max_target)
        target_humidity = (min_target + max_target) / 2

        for use_case in use_cases:
            (device_type, target_fan_speed, target_mode, target_device_power) = use_case

            if device_type == DeviceType.HUMIDIFIER:
                for humidifier in humidifiers:
                    if not humidifier.is_automatic:
                        continue

                    driver = self.humidifier_device_manager.get_driver(humidifier)

                    try:
                        if driver.get_power() != target_device_power:
                            print(f'Humidifier #{humidifier.id} power:', driver.get_power(), '->', target_device_power.value)

                        driver.set_power(target_device_power)

                        if target_device_power == DevicePower.ON:
                            if driver.get_humidity() != target_humidity:
                                print(f'Humidifier #{humidifier.id} humidity:', driver.get_humidity(), '->', target_humidity)
                                driver.set_humidity(target_humidity)

                            if driver.get_fan_speed() != target_fan_speed:
                                print(f'Humidifier #{humidifier.id} fan speed:', driver.get_fan_speed(), '->', target_fan_speed.value)
                                driver.set_fan_speed(target_fan_speed)

                            if driver.get_mode() != target_mode:
                                print(f'Humidifier #{humidifier.id} mode:', driver.get_mode(), '->', target_mode.value)
                                driver.set_mode(target_mode)

                            humidifier.power = DevicePower.ON.value
                            humidifier.target_humidity = target_humidity
                            humidifier.target_fan_speed = target_fan_speed.value
                            humidifier.target_mode = target_mode.value
                        else:
                            humidifier.power = DevicePower.OFF.value
                            humidifier.target_temperature = None
                            humidifier.target_fan_speed = None
                            humidifier.target_mode = None

                        humidifier.error = None
                    except Exception as e:
                        humidifier.error = str(e)
                    finally:
                        humidifier.save()
            elif device_type == DeviceType.DEHUMIDIFIER:
                for dehumidifier in dehumidifiers:
                    if not dehumidifier.is_automatic:
                        continue

                    driver = self.dehumidifier_device_manager.get_driver(dehumidifier)

                    try:
                        if driver.get_power() != target_device_power:
                            print(f'Dehumidifier #{humidifier.id} power:', driver.get_power(), '->', target_device_power.value)

                        driver.set_power(target_device_power)

                        if target_device_power == DevicePower.ON:
                            if driver.get_humidity() != target_humidity:
                                print(f'Dehumidifier #{dehumidifier.id} humidity:', driver.get_humidity(), '->', target_humidity)
                                driver.set_humidity(target_humidity)

                            if driver.get_fan_speed() != target_fan_speed:
                                print(f'Dehumidifier #{dehumidifier.id} fan speed:', driver.get_fan_speed(), '->', target_fan_speed.value)
                                driver.set_fan_speed(target_fan_speed)

                            if driver.get_mode() != target_mode:
                                print(f'Dehumidifier #{dehumidifier.id} mode:', driver.get_mode(), '->', target_mode.value)
                                driver.set_mode(target_mode)

                            dehumidifier.power = DevicePower.ON.value
                            dehumidifier.target_humidity = target_humidity
                            dehumidifier.target_fan_speed = target_fan_speed.value
                            dehumidifier.target_mode = target_mode.value
                        else:
                            dehumidifier.power = DevicePower.OFF.value
                            dehumidifier.target_temperature = None
                            dehumidifier.target_fan_speed = None
                            dehumidifier.target_mode = None

                        dehumidifier.error = None
                    except Exception as e:
                        dehumidifier.error = str(e)
                    finally:
                        dehumidifier.save()
            else:
                raise ValueError(f"Unknown device type: {device_type.value}")

