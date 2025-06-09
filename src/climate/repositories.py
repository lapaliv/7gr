from climate.models import Sector
from climate.enums import (
    FanSpeed,
    ConditioningMode,
    DevicePower,
    DeviceType,
    HumidityMode,
    DehumidificationMode,
    Season,
)
from climate.storages import KnowledgeStorage
from rdflib import URIRef
from datetime import date

class KnowledgeRepository:
    EX_PREFIX = "http://example.org/building#"

    def __init__(self, storage: KnowledgeStorage):
            self.storage = storage

class TemperatureCategoryRepository(KnowledgeRepository):
    def get_by_delta(self, delta: float) -> URIRef:
        result = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                SELECT ?cat
                WHERE {
                    ?cat a ex:TemperatureCategory ;
                         ex:hasMinTemperature ?min ;
                         ex:hasMaxTemperature ?max .
                    FILTER(?delta >= ?min && ?delta <= ?max)
                }
            """,
            {"delta": delta}
        )
        if not result:
            raise LookupError("No matching temperature category found")

        return result[0][0]

class HumidityCategoryRepository(KnowledgeRepository):
    def get_by_delta(self, delta: float) -> URIRef:
        result = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                SELECT ?cat
                WHERE {
                    ?cat a ex:HumidityCategory ;
                         ex:hasMinHumidity ?min ;
                         ex:hasMaxHumidity ?max .
                    FILTER(?delta >= ?min && ?delta <= ?max)
                }
            """,
            {"delta": delta}
        )
        if not result:
            raise LookupError("No matching humidity category found")

        return result[0][0]

class DensityCategoryRepository(KnowledgeRepository):
    def get_by_density(self, density: float) -> URIRef:
        result = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?category
                WHERE {
                    ?category a ex:DensityCategory ;
                            ex:hasMinDensity ?min ;
                            ex:hasMaxDensity ?max .

                    FILTER (?density >= ?min && ?density < ?max)
                }
            """,
            {"density": density}
        )
        if not result:
            raise LookupError("No matching density category found")

        return result[0][0]

class UseCaseRepository(KnowledgeRepository):
    def __init__(
        self,
        storage: KnowledgeStorage,
        temperature_category_repository: TemperatureCategoryRepository,
        density_category_repository: DensityCategoryRepository,
        humidity_category_repository: HumidityCategoryRepository,
    ):
        super().__init__(storage)
        self.temperature_category_repository = temperature_category_repository
        self.density_category_repository = density_category_repository
        self.humidity_category_repository = humidity_category_repository

    def get_by_temperature(
        self,
        current_temperature: float,
        min_target_temperature: float,
        max_target_temperature: float,
        density: float,
    ) -> list:
        delta = self._get_delta(current_temperature, min_target_temperature, max_target_temperature)
        temperature_category = self.temperature_category_repository.get_by_delta(delta)
        density_category = self.density_category_repository.get_by_density(density)

        rows = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?fan_speed ?mode ?device_power
                WHERE {
                    ?use_case a ex:ConditioningUseCase ;
                              ex:hasTemperatureCategory ?temperature_category ;
                              ex:hasDensityCategory ?density_category ;
                              ex:label ?label ;
                              ex:hasConditioningFanSpeed ?fan_speed ;
                              ex:hasConditioningMode ?mode ;
                              ex:controls ?device .

                    ?device ex:hasPower ?device_power .
                }
            """,
            {
                "temperature_category": temperature_category,
                "density_category": density_category,
            }
        )

        result = []
        for row in rows:
            (fan_speed, mode, device_power) = row

            tuple = (
                FanSpeed(fan_speed.replace(self.EX_PREFIX, '')),
                ConditioningMode(mode.replace(self.EX_PREFIX, '')),
                DevicePower(device_power.replace(self.EX_PREFIX, ''))
            )
            result.append(tuple)

        return result

    def get_by_humidity(
        self,
        current_humidity: float,
        min_target_humidity: float,
        max_target_humidity: float,
    ) -> list:
        delta = self._get_delta(current_humidity, min_target_humidity, max_target_humidity)
        humidity_category = self.humidity_category_repository.get_by_delta(delta)

        rows = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?use_case_type ?fan_speed ?mode ?device_power
                WHERE {
                    ?use_case a ?use_case_type ;
                              ex:hasHumidityCategory ?humidity_category ;
                              ex:controls ?device .

                    OPTIONAL {
                        ?use_case ex:hasHumidifyingFanSpeed ?fan_speed .
                        ?use_case ex:hasHumidityMode ?mode .
                    }
                    OPTIONAL {
                        ?use_case ex:hasDehumidificationFanSpeed ?fan_speed .
                        ?use_case ex:hasDehumidificationMode ?mode .
                    }

                    ?device ex:hasPower ?device_power .

                    FILTER (?use_case_type IN (ex:HumidifyingUseCase, ex:DehumidifyingUseCase))
                }
            """,
            {
                "humidity_category": humidity_category,
            }
        )

        result = []
        for row in rows:
            (use_case_type, fan_speed, mode, device_power) = row

            if use_case_type.endswith("HumidifyingUseCase"):
                use_case_kind = DeviceType.HUMIDIFIER
                fan_speed_enum = FanSpeed(fan_speed.replace(self.EX_PREFIX, '')) if fan_speed else None
                mode_enum = HumidityMode(mode.replace(self.EX_PREFIX, '')) if mode else None
            elif use_case_type.endswith("DehumidifyingUseCase"):
                use_case_kind = DeviceType.DEHUMIDIFIER
                fan_speed_enum = FanSpeed(fan_speed.replace(self.EX_PREFIX, '')) if fan_speed else None
                mode_enum = DehumidificationMode(mode.replace(self.EX_PREFIX, '')) if mode else None
            else:
                raise ValueError(f"Unknown use_case_type: {use_case_type}")

            device_power_enum = DevicePower(device_power.replace(self.EX_PREFIX, ''))

            tuple = (
                use_case_kind,
                fan_speed_enum,
                mode_enum,
                device_power_enum
            )
            result.append(tuple)

        return result

    def _get_delta(self, current: float, min: float, max: float) -> float:
        if current < min:
            return current - min

        if current > max:
            return current - max

        return 0.0

class SeasonRepository(KnowledgeRepository):
    def get_temperature_span(self, season: Season):
        result = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                SELECT ?minTemperature ?maxTemperature
                WHERE {
                  ?season ex:hasMinTemperature ?minTemperature ;
                          ex:hasMaxTemperature ?maxTemperature .
                }
            """,
            {'season': URIRef(f"http://example.org/building#{season.value}")}
        )

        if not result:
            raise LookupError("No matching season temperature span found")

        min_temp = result[0]['minTemperature'].toPython()
        max_temp = result[0]['maxTemperature'].toPython()

        return min_temp, max_temp

    def get_humidity_span(self, season: Season):
        result = self.storage.get(
            """
                PREFIX ex: <http://example.org/building#>
                SELECT ?minHumidity ?maxHumidity
                WHERE {
                  ?season ex:hasMinHumidity ?minHumidity ;
                          ex:hasMaxHumidity ?maxHumidity .
                }
            """,
            {'season': URIRef(f"http://example.org/building#{season.value}")}
        )

        if not result:
            raise LookupError("No matching season humidity span found")

        min_humidity = result[0]['minHumidity'].toPython()
        max_humidity = result[0]['maxHumidity'].toPython()

        return min_humidity, max_humidity

    @staticmethod
    def get_current_season(today: date = date.today()) -> Season:
        Y = today.year
        if date(Y, 12, 1) <= today or today <= date(Y, 3, 31):
            return Season.WINTER
        elif date(Y, 4, 1) <= today <= date(Y, 5, 31):
            return Season.SPRING
        elif date(Y, 6, 1) <= today <= date(Y, 8, 31):
            return Season.SUMMER
        else:
            return Season.FALL

class SectorRepository:
    def get_all(self):
        return Sector.objects.order_by("id")


class DeviceRepository:
    def get_for_sector(self, sector: Sector):
        return sector.device_set.all()
