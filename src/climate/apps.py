from django.apps import AppConfig


class ClimateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "climate"

    def ready(self):
        from .container import Container
        container = Container()
        container.wire()
        import sys
        sys.modules["container"] = container
