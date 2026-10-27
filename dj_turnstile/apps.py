from django.apps import AppConfig


class DjTurnstileConfig(AppConfig):
    name = "dj_turnstile"

    def ready(self):
        from . import checks  # noqa: F401
