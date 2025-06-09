from enum import Enum

class ConditioningMode(Enum):
    HEATING = 'heating'
    COOLING = 'cooling'
    AUTO = 'auto'

class HumidityMode(Enum):
    TURBO = 'turbo'
    AUTO = 'auto'

class DehumidificationMode(Enum):
    TURBO = 'turbo'
    AUTO = 'auto'

class DeviceType(Enum):
    CONDITIONER = 'conditioner'
    CAMERA = 'camera'
    HUMIDIFIER = 'humidifier'
    DEHUMIDIFIER = 'dehumidifier'
    TEMPERATURE_SENSOR = 'temperature_sensor'
    HUMIDITY_SENSOR = 'humidity_sensor'

class Season(Enum):
    WINTER = 'winter'
    SPRING = 'spring'
    SUMMER = 'summer'
    FALL = 'fall'

class FanSpeed(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    AUTO = 'auto'

class DevicePower(Enum):
    OFF = 'off'
    ON = 'on'
