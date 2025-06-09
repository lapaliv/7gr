from climate.repositories import SectorRepository, DeviceRepository, UseCaseRepository, SeasonRepository
from climate.managers import ConditionerDeviceManager, CameraDeviceManager
from climate.enums import DeviceType
from climate.models import Sector
from climate.wrappers import ComputerVision
import statistics

from . import models, repositories

class GetAverageDestinyFromCamerasFeature:
    def __init__(
        self,
        camera_device_manager: CameraDeviceManager,
        computer_vision: ComputerVision,
    ):
        self.camera_device_manager = camera_device_manager
        self.computer_vision = computer_vision


    def handle(self, cameras: list) -> float | None:
        photos = []

        for camera in cameras:
            driver = self.camera_device_manager.get_driver(camera)
            photo = driver.get_photo()
            photos.append(photo)

        values = []
        for photo in photos:
            destiny = self.computer_vision.get_number_of_people(photo)
            values.append(destiny)

        if values:
            return statistics.mean(values)

        return None
