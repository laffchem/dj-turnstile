from django.core.checks import run_checks

TESTING_ID = "django_cf_turnstile.turnstile_test_key_error"
MISSING_ID = "django_cf_turnstile.turnstile_keys_missing"


def _ids():
    return [m.id for m in run_checks()]


def test_error_when_keys_missing(settings):
    del settings.TURNSTILE_SITEKEY
    del settings.TURNSTILE_SECRET
    assert MISSING_ID in _ids()


def test_no_messages_when_keys_set(settings):
    ids = _ids()
    assert MISSING_ID not in ids
    assert TESTING_ID not in ids


def test_warning_when_testing_enabled(settings):
    del settings.TURNSTILE_SITEKEY
    del settings.TURNSTILE_SECRET
    settings.TURNSTILE_TESTING = True
    ids = _ids()
    assert TESTING_ID in ids
    assert MISSING_ID not in ids
