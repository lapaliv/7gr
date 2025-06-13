from enum import Enum

class BaseStrEnum(str):
    @classmethod
    def choices(cls):
        return [(key.value, key.name.replace('_', ' ').title()) for key in cls]

class ConditioningMode(BaseStrEnum, Enum):
    HEATING = 'heating'
    COOLING = 'cooling'
    AUTO = 'auto'

class HumidityMode(BaseStrEnum, Enum):
    TURBO = 'turbo'
    AUTO = 'auto'

class DehumidificationMode(BaseStrEnum, Enum):
    TURBO = 'turbo'
    AUTO = 'auto'

class DeviceType(BaseStrEnum, Enum):
    CONDITIONER = 'conditioner'
    CAMERA = 'camera'
    HUMIDIFIER = 'humidifier'
    DEHUMIDIFIER = 'dehumidifier'
    TEMPERATURE_SENSOR = 'temperature_sensor'
    HUMIDITY_SENSOR = 'humidity_sensor'

class Season(BaseStrEnum, Enum):
    WINTER = 'winter'
    SPRING = 'spring'
    SUMMER = 'summer'
    FALL = 'fall'

class FanSpeed(BaseStrEnum, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    AUTO = 'auto'

class DevicePower(BaseStrEnum, Enum):
    OFF = 'off'
    ON = 'on'
