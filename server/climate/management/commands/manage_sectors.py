from django.core.management.base import BaseCommand
import statistics
import math

from climate.container import Container
from climate.enums import Season, DeviceType, DevicePower
from climate.models import Sector
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

        self.sector_service = Container.sector_service()

    def handle(self, *args, **kwargs):
        sectors_offset = 0
        sectors_limit = 100

        while True:
            sectors = self.sector_repository.get_all(sectors_offset, sectors_limit)
            season = self.season_repository.get_current_season()

            for sector in sectors:
                print("-" * 10, 'SECTOR:', sector.name, '-' * 10)
                print("-" * 3, 'State', '-' * 3)

                current_density = self.sector_service.get_current_density(sector)
                print('Average density:', 'None' if current_density is None else f'{current_density} people')

                current_temperature = self.sector_service.get_current_temperature(sector)
                print('Average humidity:', 'None' if current_temperature is None else f'{current_temperature}°C')

                current_humidity = self.sector_service.get_current_humidity(sector)
                print('Average humidity:', 'None' if current_humidity is None else f'{current_humidity}%')

                if current_temperature or current_humidity:
                    print("-" * 3, 'Updates', '-' * 3)

                if current_density:
                    self._manage_fan(sector, current_density)

                if current_temperature and current_density:
                    self._manage_temperature(sector, season, current_density, current_temperature)

                if current_humidity:
                    self._manage_humidity(sector, season, current_humidity)

            if len(sectors) < sectors_limit:
                break

    def _manage_temperature(self, sector: Sector, season: Season, density: float, current_temperature: float):
        devices = self.device_repository.get_for_sector(sector)
        (min_target, max_target) = self.season_repository.get_temperature_span(season)
        target_temperature = (min_target + max_target) / 2
        use_cases = self.use_case_repository.get_conditioning_use_cases(current_temperature, min_target, max_target, density)

        for device in devices:
            if not device.is_automatic or device.power == DevicePower.OFF.value:
                continue

            if device.type != DeviceType.CONDITIONER.value:
                continue

            driver = self.conditioner_device_manager.get_driver(device)

            for use_case in use_cases:
                (target_fan_speed, target_mode, target_device_power) = use_case

                try:
                    if driver.get_power() != target_device_power:
                        print(f'Conditioner #{device.id} power:', DevicePower(driver.get_power()), '->', target_device_power.value)

                    driver.set_power(target_device_power)

                    if target_device_power == DevicePower.ON:
                        if driver.get_temperature() != target_temperature:
                            print(f'Conditioner #{device.id} temperature:', driver.get_temperature(), '->', target_temperature)
                            driver.set_temperature(target_temperature)

                        if driver.get_fan_speed() != target_fan_speed:
                            print(f'Conditioner #{device.id} fan speed:', driver.get_fan_speed(), '->', target_fan_speed.value)
                            driver.set_fan_speed(target_fan_speed)

                        if driver.get_mode() != target_mode:
                            print(f'Conditioner #{device.id} mode:', driver.get_mode(), '->', target_mode.value)
                            driver.set_mode(target_mode)

                        device.power = DevicePower.ON.value
                        device.target_temperature = target_temperature
                        device.target_fan_speed = target_fan_speed.value
                        device.target_mode = target_mode.value
                    else:
                        device.power = DevicePower.OFF.value
                        device.target_temperature = None
                        device.target_fan_speed = None
                        device.target_mode = None
                    device.error = None
                except Exception as e:
                    device.error = str(e)
                finally:
                    device.save()

    def _manage_fan(self, sector: Sector, density: float):
        devices = self.device_repository.get_for_sector(sector)
        use_cases = self.use_case_repository.get_fan_use_case_by_density(density)

        for device in devices:
            if not device.is_automatic or device.power == DevicePower.OFF.value:
                continue

            if device.type != DeviceType.FAN.value:
                continue

            driver = self.fan_device_manager.get_driver(device)

            for use_case in use_cases:
                (target_speed, target_device_power) = use_case

                try:
                    if driver.get_power() != target_device_power:
                        print(f'Fan #{device.id} power:', DevicePower(driver.get_power()), '->', target_device_power.value)

                    driver.set_power(target_device_power)

                    if target_device_power == DevicePower.ON:
                        if driver.get_speed() != target_speed:
                            print(f'Fan #{device.id} speed:', driver.get_speed(), '->', target_speed.value)
                            driver.set_speed(target_speed)

                        device.power = DevicePower.ON.value
                        device.current_fan_speed = driver.get_speed()
                        device.target_fan_speed = target_speed.value
                    else:
                        device.power = DevicePower.OFF.value
                        device.current_fan_speed = None
                        device.target_fan_speed = None

                    device.error = None
                except Exception as e:
                    device.error = str(e)
                finally:
                    device.save()

    def _manage_humidity(self, sector: Sector, season: Season, current_humidity: float):
        devices = self.device_repository.get_for_sector(sector)
        (min_target, max_target) = self.season_repository.get_humidity_span(season)
        use_cases = self.use_case_repository.get_humidity_use_cases(current_humidity, min_target, max_target)
        target_humidity = (min_target + max_target) / 2

        for device in devices:
            if not device.is_automatic or device.power == DevicePower.OFF.value:
                continue

            if device.type == DeviceType.HUMIDIFIER.value:
                driver = self.humidifier_device_manager.get_driver(device)

                for use_case in use_cases:
                    (device_type, target_fan_speed, target_mode, target_device_power) = use_case

                    if device_type != DeviceType.HUMIDIFIER:
                        continue

                    try:
                        if driver.get_power() != target_device_power:
                            print(f'Humidifier #{device.id} power:', driver.get_power(), '->', target_device_power.value)

                        driver.set_power(target_device_power)

                        if target_device_power == DevicePower.ON:
                            if driver.get_humidity() != target_humidity:
                                print(f'Humidifier #{device.id} humidity:', driver.get_humidity(), '->', target_humidity)
                                driver.set_humidity(target_humidity)

                            if driver.get_fan_speed() != target_fan_speed:
                                print(f'Humidifier #{device.id} fan speed:', driver.get_fan_speed(), '->', target_fan_speed.value)
                                driver.set_fan_speed(target_fan_speed)

                            if driver.get_mode() != target_mode:
                                print(f'Humidifier #{device.id} mode:', driver.get_mode(), '->', target_mode.value)
                                driver.set_mode(target_mode)

                            device.power = DevicePower.ON.value
                            device.target_humidity = target_humidity
                            device.target_fan_speed = target_fan_speed.value
                            device.target_mode = target_mode.value
                        else:
                            device.power = DevicePower.OFF.value
                            device.target_temperature = None
                            device.target_fan_speed = None
                            device.target_mode = None

                        device.error = None
                    except Exception as e:
                        device.error = str(e)
                    finally:
                        device.save()

            elif device.type == DeviceType.DEHUMIDIFIER.value:
                driver = self.dehumidifier_device_manager.get_driver(device)

                for use_case in use_cases:
                    (device_type, target_fan_speed, target_mode, target_device_power) = use_case

                    if device_type != DeviceType.DEHUMIDIFIER:
                        continue

                    try:
                        if driver.get_power() != target_device_power:
                            print(f'Dehumidifier #{device.id} power:', driver.get_power(), '->', target_device_power.value)

                        driver.set_power(target_device_power)

                        if target_device_power == DevicePower.ON:
                            if driver.get_humidity() != target_humidity:
                                print(f'Dehumidifier #{device.id} humidity:', driver.get_humidity(), '->', target_humidity)
                                driver.set_humidity(target_humidity)

                            if driver.get_fan_speed() != target_fan_speed:
                                print(f'Dehumidifier #{device.id} fan speed:', driver.get_fan_speed(), '->', target_fan_speed.value)
                                driver.set_fan_speed(target_fan_speed)

                            if driver.get_mode() != target_mode:
                                print(f'Dehumidifier #{device.id} mode:', driver.get_mode(), '->', target_mode.value)
                                driver.set_mode(target_mode)

                            device.power = DevicePower.ON.value
                            device.target_humidity = target_humidity
                            device.target_fan_speed = target_fan_speed.value
                            device.target_mode = target_mode.value
                        else:
                            device.power = DevicePower.OFF.value
                            device.target_temperature = None
                            device.target_fan_speed = None
                            device.target_mode = None

                        device.error = None
                    except Exception as e:
                        device.error = str(e)
                    finally:
                        device.save()
