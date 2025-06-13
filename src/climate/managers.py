from climate.models import Device
from climate.wrappers import (
    TemperatureSensor,
    DummyTemperatureSensor,
    Conditioner,
    DummyConditioner,
    Camera,
    DummyCamera,
    ComputerVision,
    DummyComputerVision,
    HumiditySensor,
    DummyHumiditySensor,
    Humidifier,
    DummyHumidifier,
    Dehumidifier,
    DummyDehumidifier,
)
from climate.enums import ConditioningMode, FanSpeed, DevicePower, HumidityMode

class TemperatureSensorDeviceManager:
    def get_driver(self, sensor: Device) -> TemperatureSensor:
        return DummyTemperatureSensor(
            temperature = 20.0 if sensor.current_temperature is None else float(sensor.current_temperature)
        )

class ConditionerDeviceManager:
    def get_driver(self, conditioner: Device) -> Conditioner:
        return DummyConditioner(
            temperature = 25.0 if conditioner.current_temperature is None else float(conditioner.current_temperature),
            fan_speed = FanSpeed.MEDIUM if conditioner.current_fan_speed is None else conditioner.current_fan_speed,
            mode = HumidityMode.AUTO if conditioner.current_mode is None else conditioner.current_mode,
            power = conditioner.power
        )

class CameraDeviceManager:
    def get_driver(self, camera: Device) -> Camera:
        return DummyCamera(url = "https://personal.ie.cuhk.edu.hk/~ccloy/images/shopping_mall.jpg")

class HumiditySensorDeviceManager:
    def get_driver(self, sensor: Device) -> HumiditySensor:
        return DummyHumiditySensor(
            humidity = 50.0 if sensor.current_humidity is None else float(sensor.current_humidity),
        )

class HumidifierDeviceManager:
    def get_driver(self, humidifier: Device) -> Humidifier:
        return DummyHumidifier(
            humidity = 50.0 if humidifier.current_humidity is None else float(humidifier.current_humidity),
            fan_speed = FanSpeed.MEDIUM if humidifier.current_fan_speed is None else humidifier.current_fan_speed,
            mode = HumidityMode.AUTO if humidifier.current_mode is None else humidifier.current_mode,
            power = humidifier.power
        )

class DehumidifierDeviceManager:
    def get_driver(self, dehumidifier: Device) -> Dehumidifier:
        return DummyDehumidifier(
            humidity = 50.0 if dehumidifier.current_humidity is None else float(dehumidifier.current_humidity),
            fan_speed = FanSpeed.MEDIUM if dehumidifier.current_fan_speed is None else dehumidifier.current_fan_speed,
            mode = HumidityMode.AUTO if dehumidifier.current_mode is None else dehumidifier.current_mode,
            power = dehumidifier.power
        )
