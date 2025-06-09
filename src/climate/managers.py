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
        return DummyTemperatureSensor(temperature = 20.0) # TODO: replace with the real driver

class ConditionerDeviceManager:
    def get_driver(self, conditioner: Device) -> Conditioner:
        return DummyConditioner(temperature = 25.0, fan_speed = FanSpeed.MEDIUM, mode = ConditioningMode.AUTO, power = DevicePower.ON) # TODO: replace with the real driver

class CameraDeviceManager:
    def get_driver(self, camera: Device) -> Camera:
        return DummyCamera(url = "https://personal.ie.cuhk.edu.hk/~ccloy/images/shopping_mall.jpg") # TODO: replace with the real driver

class HumiditySensorDeviceManager:
    def get_driver(self, sensor: Device) -> HumiditySensor:
        return DummyHumiditySensor(humidity = 40.0) # TODO: replace with the real driver

class HumidifierDeviceManager:
    def get_driver(self, humidifier: Device) -> Humidifier:
        return DummyHumidifier(humidity = 50.0, fan_speed = FanSpeed.MEDIUM, mode = HumidityMode.AUTO, power = DevicePower.ON) # TODO: replace with the real driver

class DehumidifierDeviceManager:
    def get_driver(self, dehumidifier: Device) -> Dehumidifier:
        return DummyDehumidifier(humidity = 50.0, fan_speed = FanSpeed.MEDIUM, mode = HumidityMode.AUTO, power = DevicePower.OFF) # TODO: replace with the real driver
