from django.apps import apps
from django.core.signals import setting_changed
import sys

def init_container(*args, **kwargs):
    if apps.ready:
        from climate.container import Container
        container = Container()
        container.wire()
        sys.modules["container"] = container

setting_changed.connect(init_container)
