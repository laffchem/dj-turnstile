import pytest
from django.core.exceptions import ImproperlyConfigured

from dj_turnstile.widgets import TurnstileWidget


def test_widget_context_contains_sitekey(settings):
    """Ensure widget is correctly pulling sitekey from settings into context"""
    settings.TURNSTILE_SITEKEY = "fake_site_key_123"
    widget = TurnstileWidget()

    context = widget.get_context("turnstile", None, {})
    assert context["widget"]["sitekey"] == "fake_site_key_123"


def test_value_from_datadict():
    """Ensure the widget specifically looks for the cf-turnstile response."""
    widget = TurnstileWidget()
    mock_post_data = {
        "other_field": "hello",
        "cf-turnstile-response": "intercepted_token",
    }
    value = widget.value_from_datadict(mock_post_data, None, "turnstile")
    assert value == "intercepted_token"


def test_missing_sitekey_raises(settings):
    del settings.TURNSTILE_SITEKEY
    with pytest.raises(ImproperlyConfigured, match="TURNSTILE_SITEKEY"):
        TurnstileWidget().get_context("t", None, {})


def test_testing_mode_uses_dummy_sitekey(settings):
    del settings.TURNSTILE_SITEKEY
    settings.TURNSTILE_TESTING = True
    context = TurnstileWidget().get_context("t", None, {})
    assert context["widget"]["sitekey"] == "1x00000000000000000000AA"


def test_options_render_as_data_attrs_and_api_params():
    widget = TurnstileWidget(
        action="login",
        theme="dark",
        size="compact",
        language="de",
        sitekey="mine",
        api_params={"render": "explicit"},
    )
    html = widget.render("turnstile", None)
    assert 'data-theme="dark"' in html
    assert 'data-size="compact"' in html
    assert 'data-language="de"' in html
    assert 'data-action="login"' in html
    assert 'data-sitekey="mine"' in html
    assert "api.js?render=explicit" in html


def test_no_required_attribute():
    assert TurnstileWidget().use_required_attribute(None) is False
