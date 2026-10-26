from django.apps import AppConfig


class DjangoCfTurnstileConfig(AppConfig):
    name = "django_cf_turnstile"

    def ready(self):
        from . import checks  # noqa: F401
