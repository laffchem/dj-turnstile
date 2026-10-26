"""Accessors for the TURNSTILE_* settings, read lazily so tests can override them."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from . import constants


def is_testing():
    return bool(getattr(settings, "TURNSTILE_TESTING", False))


def _get_key(name, test_value):
    value = getattr(settings, name, None)
    if value:
        return value
    if is_testing():
        return test_value
    raise ImproperlyConfigured(
        f"{name} is not set. Add it to your Django settings, or set "
        "TURNSTILE_TESTING = True to use Cloudflare's dummy test keys."
    )


def get_sitekey():
    return _get_key("TURNSTILE_SITEKEY", constants.TEST_SITEKEY)


def get_secret():
    return _get_key("TURNSTILE_SECRET", constants.TEST_SECRET)


def keys_missing():
    return [
        name
        for name in ("TURNSTILE_SITEKEY", "TURNSTILE_SECRET")
        if not getattr(settings, name, None)
    ]


def get_verify_url():
    return getattr(settings, "TURNSTILE_VERIFY_URL", constants.VERIFY_URL)


def get_api_url():
    return getattr(settings, "TURNSTILE_API_URL", constants.API_URL)


def get_timeout():
    return getattr(
        settings, "TURNSTILE_VERIFY_REQUEST_TIMEOUT", constants.DEFAULT_TIMEOUT
    )


def get_proxies():
    return getattr(settings, "TURNSTILE_PROXIES", None)
