from dependency_injector import containers, providers
from . import storages
from climate.storages import N3KnowledgeStorage
from climate.repositories import (
    UseCaseRepository,
    SeasonRepository,
    TemperatureCategoryRepository,
    DensityCategoryRepository,
    SectorRepository,
    DeviceRepository,
    HumidityCategoryRepository,
)
from climate.managers import (
    ConditionerDeviceManager,
    CameraDeviceManager,
    HumidifierDeviceManager,
    DehumidifierDeviceManager,
    TemperatureSensorDeviceManager,
    HumiditySensorDeviceManager,
)
from climate.features import (
    GetAverageDestinyFromCamerasFeature
)
from climate.wrappers import ComputerVision, DummyComputerVision
from pathlib import Path

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        "climate.management.commands.manage_sectors",
        "climate.controllers",
        "climate.features",
        "climate.repositories",
        "climate.storages",
        "climate.views",
    ])

    base_path = Path(__file__).resolve().parent.parent

    # Storages
    n3_knowledge_path = base_path / 'knowledgebase.n3'
    n3_knowledge_storage = providers.Singleton(N3KnowledgeStorage, n3_knowledge_path.resolve())
    knowledge_storage = providers.Delegate(n3_knowledge_storage)

    # Repositories
    season_repository = providers.Singleton(SeasonRepository,storage=knowledge_storage())
    temperature_category_repository = providers.Singleton(TemperatureCategoryRepository,storage=knowledge_storage())
    density_category_repository = providers.Singleton(DensityCategoryRepository,storage=knowledge_storage())
    humidity_category_repository = providers.Singleton(HumidityCategoryRepository,storage=knowledge_storage())
    use_case_repository = providers.Singleton(
        UseCaseRepository,
        storage = knowledge_storage(),
        temperature_category_repository = temperature_category_repository(),
        density_category_repository = density_category_repository(),
        humidity_category_repository = humidity_category_repository(),
    )
    sector_repository = providers.Singleton(SectorRepository)
    device_repository = providers.Singleton(DeviceRepository)

    # Managers
    conditioner_device_manager = providers.Singleton(ConditionerDeviceManager)
    camera_device_manager = providers.Singleton(CameraDeviceManager)
    humidifier_device_manager = providers.Singleton(HumidifierDeviceManager)
    dehumidifier_device_manager = providers.Singleton(DehumidifierDeviceManager)
    temperature_sensor_device_manager = providers.Singleton(TemperatureSensorDeviceManager)
    humidity_sensor_device_manager = providers.Singleton(HumiditySensorDeviceManager)

    # Device drivers
    dummy_computer_vision = providers.Singleton(DummyComputerVision, 30.0)
    computer_vision = providers.Delegate(dummy_computer_vision)

    # Features
    get_average_destiny_from_cameras_feature = providers.Singleton(GetAverageDestinyFromCamerasFeature, camera_device_manager = camera_device_manager(), computer_vision = computer_vision())
