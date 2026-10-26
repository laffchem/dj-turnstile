from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def turnstile_keys(settings):
    settings.TURNSTILE_SITEKEY = "test_sitekey"
    settings.TURNSTILE_SECRET = "test_secret"


@pytest.fixture
def mock_post():
    with patch("niquests.Session.post") as mock:
        yield mock
