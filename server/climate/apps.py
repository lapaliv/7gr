from django.apps import AppConfig
from pathlib import Path

class ClimateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "climate"

    _container_initialized = False

#     def ready(self):
#         if self._container_initialized:
#             return
#
#         self._container_initialized = True
#
#         from .container import Container
#         container = Container()
# #         container.base_path = Path(__file__).resolve().parent.parent
#         container.wire()
#         import sys
#         sys.modules["container"] = container
