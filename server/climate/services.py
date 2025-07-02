import statistics
import math

from climate.enums import DeviceType
from climate.models import Sector, HistoricalData, Device
from climate.repositories import DeviceRepository, HistoricalDataRepository
from climate.managers import (
    ConditionerDeviceManager,
    CameraDeviceManager,
    HumiditySensorDeviceManager,
    HumidifierDeviceManager,
    DehumidifierDeviceManager,
    TemperatureSensorDeviceManager,
)
from climate.wrappers import ComputerVision

class SectorService:
    def __init__(
        self,
        device_repository: DeviceRepository,
        conditioner_device_manager: ConditionerDeviceManager,
        camera_device_manager: CameraDeviceManager,
        computer_vision: ComputerVision,
        humidity_sensor_device_manager: HumiditySensorDeviceManager,
        humidifier_device_manager: HumidifierDeviceManager,
        dehumidifier_device_manager: DehumidifierDeviceManager,
        temperature_sensor_device_manager: TemperatureSensorDeviceManager,
        historical_data_repository: HistoricalDataRepository,
    ):
        self.device_repository = device_repository
        self.conditioner_device_manager = conditioner_device_manager
        self.camera_device_manager = camera_device_manager
        self.computer_vision = computer_vision
        self.humidity_sensor_device_manager = humidity_sensor_device_manager
        self.humidifier_device_manager = humidifier_device_manager
        self.dehumidifier_device_manager = dehumidifier_device_manager
        self.temperature_sensor_device_manager = temperature_sensor_device_manager
        self.historical_data_repository = historical_data_repository

    def get_current_density(self, sector: Sector) -> float | None:
        devices = self.device_repository.get_for_sector(sector)

        values = []

        for device in devices:
            if device.type != DeviceType.CAMERA.value:
                continue

            try:
                driver = self.camera_device_manager.get_driver(device)

                photo = driver.get_photo()
                density = self.computer_vision.get_number_of_people(photo)
                values.append(density)

                device.current_density = density

                self._create_historical_data(device)
            except Exception as e:
                device.error = str(e)
            finally:
                device.save()

        if len(values) > 0:
            result = statistics.mean(values)

            return math.floor(result * 100) / 100

        return None

    def get_current_temperature(self, sector: Sector) -> float | None:
        devices = self.device_repository.get_for_sector(sector)
        values = []

        for device in devices:
            driver = None

            if device.type == DeviceType.CONDITIONER.value:
                driver = self.conditioner_device_manager.get_driver(device)
            elif device.type == DeviceType.TEMPERATURE_SENSOR.value:
                driver = self.temperature_sensor_device_manager.get_driver(device)

            if driver == None:
                continue

            try:
                temperature = driver.get_temperature()
                values.append(temperature)

                device.current_temperature = temperature

                if device.type == DeviceType.CONDITIONER.value:
                    device.current_fan_speed = driver.get_fan_speed()
                    device.current_mode = driver.get_mode()
                elif device.type == DeviceType.TEMPERATURE_SENSOR.value:
                    device.current_fan_speed = None
                device.current_mode = None

                self._create_historical_data(device)
            except Exception as e:
                device.error = str(e)
            finally:
                device.save()

        if len(values) > 0:
            result = statistics.mean(values)

            return math.floor(result * 100) / 100

        return None

    def get_current_humidity(self, sector: Sector) -> float | None:
        devices = self.device_repository.get_for_sector(sector)
        values = []

        for device in devices:
            driver = None

            if device.type == DeviceType.HUMIDITY_SENSOR.value:
                driver = self.humidity_sensor_device_manager.get_driver(device)
            elif device.type == DeviceType.HUMIDIFIER.value:
                driver = self.humidifier_device_manager.get_driver(device)
            elif device.type == DeviceType.DEHUMIDIFIER.value:
                driver = self.dehumidifier_device_manager.get_driver(device)

            if driver == None:
                continue

            try:
                humidity = driver.get_humidity()
                values.append(humidity)

                device.current_humidity = humidity

                if device.type == DeviceType.HUMIDITY_SENSOR.value:
                    device.current_fan_speed = None
                    device.current_mode = None
                elif device.type == DeviceType.HUMIDIFIER.value or device.type == DeviceType.DEHUMIDIFIER.value:
                    device.current_fan_speed = driver.get_fan_speed()
                    device.current_mode = driver.get_mode()

                self._create_historical_data(device)
            except Exception as e:
                device.error = str(e)
            finally:
                device.save()

        if len(values) > 0:
            result = statistics.mean(values)

            return math.floor(result * 100) / 100

        return None

    def _create_historical_data(self, device: Device):
        last_historical_data = self.historical_data_repository.get_last_for_device(device)

        if (
            last_historical_data is not None and
            last_historical_data.temperature == device.current_temperature and
            last_historical_data.density == device.current_density and
            last_historical_data.humidity == device.current_humidity and
            last_historical_data.fan_speed == device.current_fan_speed and
            last_historical_data.mode == device.current_mode and
            last_historical_data.power == device.power
        ):
            return

        HistoricalData.objects.create(
            device = device,
            density = device.current_density,
            temperature = device.current_temperature,
            humidity = device.current_humidity,
            fan_speed = device.current_fan_speed,
            mode = device.current_mode,
            power = device.power
        )
