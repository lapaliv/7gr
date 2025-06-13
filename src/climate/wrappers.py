from abc import ABC, abstractmethod
from . import enums
from PIL import Image
from io import BytesIO
import requests

class TemperatureSensor(ABC):
    @abstractmethod
    def get_temperature(self) -> float:
        pass

class Conditioner(TemperatureSensor):
    @abstractmethod
    def get_temperature(self) -> float:
        pass

    @abstractmethod
    def set_temperature(self, temperature: float):
        pass

    @abstractmethod
    def get_fan_speed(self) -> enums.FanSpeed:
        pass

    @abstractmethod
    def set_fan_speed(self, fan_speed: enums.FanSpeed):
        pass

    @abstractmethod
    def get_mode(self) -> enums.ConditioningMode:
        pass

    @abstractmethod
    def set_mode(self, mode: enums.ConditioningMode):
        pass

    @abstractmethod
    def get_power(self) -> enums.DevicePower:
        pass

    @abstractmethod
    def set_power(self, power: enums.DevicePower):
        pass

class HumiditySensor(ABC):
    @abstractmethod
    def get_humidity(self) -> float:
        pass

class Dehumidifier(HumiditySensor):
    @abstractmethod
    def set_humidity(self, humidity: float):
        pass

    @abstractmethod
    def get_fan_speed(self) -> enums.FanSpeed:
        pass

    @abstractmethod
    def set_fan_speed(self, fan_speed: enums.FanSpeed):
        pass

    @abstractmethod
    def get_mode(self) -> enums.HumidityMode:
        pass

    @abstractmethod
    def set_mode(self, mode: enums.HumidityMode):
        pass

    @abstractmethod
    def get_power(self) -> enums.DevicePower:
        pass

    @abstractmethod
    def set_power(self, power: enums.DevicePower):
        pass

class Humidifier(HumiditySensor):
    @abstractmethod
    def set_humidity(self, humidity: float):
        pass

    @abstractmethod
    def get_fan_speed(self) -> enums.FanSpeed:
        pass

    @abstractmethod
    def set_fan_speed(self, fan_speed: enums.FanSpeed):
        pass

    @abstractmethod
    def get_mode(self) -> enums.HumidityMode:
        pass

    @abstractmethod
    def set_mode(self, mode: enums.HumidityMode):
        pass

    @abstractmethod
    def get_power(self) -> enums.DevicePower:
        pass

    @abstractmethod
    def set_power(self, power: enums.DevicePower):
        pass

class Camera(ABC):
    @abstractmethod
    def get_photo(self) -> Image.Image:
        pass

class DummyTemperatureSensor(TemperatureSensor):
    def __init__(self, temperature: float):
        self.temperature = temperature

    def get_temperature(self) -> float:
        return self.temperature

class DummyConditioner(Conditioner):
    def __init__(self, temperature: float, fan_speed: enums.FanSpeed, mode: enums.ConditioningMode, power: enums.DevicePower):
        self.temperature = temperature
        self.fan_speed = fan_speed
        self.mode = mode
        self.power = power

    def get_temperature(self) -> float:
        return self.temperature

    def set_temperature(self, temperature: float):
        self.temperature = temperature

    def get_fan_speed(self) -> enums.FanSpeed:
        return self.fan_speed

    def set_fan_speed(self, fan_speed: enums.FanSpeed):
        if self.fan_speed != fan_speed:
            self.fan_speed = fan_speed

    def get_mode(self) -> enums.ConditioningMode:
        return self.mode

    def set_mode(self, mode: enums.ConditioningMode):
        if self.mode != mode:
            self.mode = mode

    def get_power(self) -> enums.DevicePower:
        return self.power

    def set_power(self, power: enums.DevicePower):
        if self.power != power:
            self.power = power

class DummyCamera(Camera):
    def __init__(self, url: str):
        self.url = url

    def get_photo(self) -> Image.Image:
        response = requests.get(self.url)
        return Image.open(BytesIO(response.content))

class ComputerVision:
    @abstractmethod
    def get_number_of_people(self, image: Image.Image) -> float:
        pass

class DummyComputerVision(ComputerVision):
    def __init__(self, destiny: float):
        self.destiny = destiny

    def get_number_of_people(self, image: Image.Image) -> float:
        return self.destiny

class DummyHumidifier(Humidifier):
    def __init__(self, humidity: float, fan_speed: enums.FanSpeed, mode: enums.HumidityMode, power: enums.DevicePower):
        self.humidity = humidity
        self.fan_speed = fan_speed
        self.mode = mode
        self.power = power

    def get_humidity(self) -> float:
        return self.humidity

    def set_humidity(self, humidity: float):
        if self.humidity != humidity:
            self.humidity = humidity

    def get_fan_speed(self) -> enums.FanSpeed:
        return self.fan_speed

    def set_fan_speed(self, fan_speed: enums.FanSpeed):
        if self.fan_speed != fan_speed:
            self.fan_speed = fan_speed

    def get_mode(self) -> enums.HumidityMode:
        return self.mode

    def set_mode(self, mode: enums.HumidityMode):
        if self.mode != mode:
            self.mode = mode

    def get_power(self) -> enums.DevicePower:
        return self.power

    def set_power(self, power: enums.DevicePower):
        if self.power != power:
            self.power = power

class DummyHumiditySensor(HumiditySensor):
    def __init__(self, humidity: float):
        self.humidity = humidity

    def get_humidity(self) -> float:
        return self.humidity

class DummyDehumidifier(Dehumidifier):
    def __init__(self, humidity: float, fan_speed: enums.FanSpeed, mode: enums.HumidityMode, power: enums.DevicePower):
        self.humidity = humidity
        self.fan_speed = fan_speed
        self.mode = mode
        self.power = power

    def get_humidity(self) -> float:
        return self.humidity

    def set_humidity(self, humidity: float):
        if self.humidity != humidity:
            self.humidity = humidity

    def get_fan_speed(self) -> enums.FanSpeed:
        return self.fan_speed

    def set_fan_speed(self, fan_speed: enums.FanSpeed):
        if self.fan_speed != fan_speed:
            self.fan_speed = fan_speed

    def get_mode(self) -> enums.HumidityMode:
        return self.mode

    def set_mode(self, mode: enums.HumidityMode):
        if self.mode != mode:
            self.mode = mode

    def get_power(self) -> enums.DevicePower:
        return self.power

    def set_power(self, power: enums.DevicePower):
        if self.power != power:
            self.power = power
