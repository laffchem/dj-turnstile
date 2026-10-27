import niquests
import pytest
from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError

from dj_turnstile.fields import TurnstileField


class DummyForm(forms.Form):
    turnstile = TurnstileField()


def test_clean_raises_improperly_configured_if_secret_missing(settings):
    """A missing secret is a developer error, not a user-facing validation error."""
    settings.TURNSTILE_SECRET = ""
    with pytest.raises(ImproperlyConfigured, match="TURNSTILE_SECRET"):
        TurnstileField().clean("some_token")


def test_testing_mode_uses_dummy_secret(settings, mock_post):
    del settings.TURNSTILE_SECRET
    settings.TURNSTILE_TESTING = True
    mock_post.return_value.json.return_value = {"success": True}
    TurnstileField().clean("tok")
    assert (
        mock_post.call_args.kwargs["data"]["secret"]
        == "1x0000000000000000000000000000000AA"
    )


def test_testing_mode_prefers_real_secret(settings, mock_post):
    settings.TURNSTILE_TESTING = True
    mock_post.return_value.json.return_value = {"success": True}
    TurnstileField().clean("tok")
    assert mock_post.call_args.kwargs["data"]["secret"] == "test_secret"


@pytest.mark.parametrize(
    "cf_response,is_valid",
    [
        ({"success": True}, True),
        ({"success": False, "error-codes": ["invalid-input-response"]}, False),
    ],
    ids=["success", "invalid_token"],
)
def test_clean_against_cloudflare_response(settings, mock_post, cf_response, is_valid):
    """Ensure the field's outcome matches what Cloudflare's siteverify API reports."""
    settings.TURNSTILE_SECRET = "fake_secret_key"
    mock_post.return_value.json.return_value = cf_response

    field = TurnstileField()
    if is_valid:
        assert field.clean("valid_cloudflare_token") == "valid_cloudflare_token"
    else:
        with pytest.raises(ValidationError, match="Turnstile verification failed"):
            field.clean("invalid_token")

    mock_post.assert_called_once()
    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs["data"]["secret"] == "fake_secret_key"


def test_clean_fails_gracefully_on_network_timeout(settings, mock_post):
    """Ensure the field doesn't crash the server if cloudflare is down"""
    settings.TURNSTILE_SECRET = "fake_secret_key"
    mock_post.side_effect = niquests.exceptions.RequestException("DNS lookup failed")

    field = TurnstileField()
    with pytest.raises(
        ValidationError, match="Verification service is currently unavailable"
    ):
        field.clean("some_token")


def test_form_integration(settings, mock_post):
    """Test the field end-to-end within a django form"""
    settings.TURNSTILE_SECRET = "fake_secret_key"
    mock_post.return_value.json.return_value = {"success": True}

    form = DummyForm({"cf-turnstile-response": "valid_token"})

    assert form.is_valid()
    assert form.cleaned_data["turnstile"] == "valid_token"


def test_field_kwargs_override_settings(settings, mock_post):
    """private_key/remote_ip kwargs take precedence and are forwarded."""
    settings.TURNSTILE_SECRET = "from_settings"
    mock_post.return_value.json.return_value = {"success": True}

    TurnstileField(private_key="from_kwarg", remote_ip="1.1.1.1").clean("tok")

    data = mock_post.call_args.kwargs["data"]
    assert data["secret"] == "from_kwarg"
    assert data["remoteip"] == "1.1.1.1"


def test_config_errors_do_not_look_like_bad_tokens(settings, mock_post):
    """A rejected secret is a captcha_error, not the user's fault."""
    settings.TURNSTILE_SECRET = "bad"
    mock_post.return_value.json.return_value = {
        "success": False,
        "error-codes": ["invalid-input-secret"],
    }
    with pytest.raises(ValidationError) as exc:
        TurnstileField().clean("tok")
    assert exc.value.code == "captcha_error"


def test_action_mismatch_is_invalid(settings, mock_post):
    settings.TURNSTILE_SECRET = "s"
    mock_post.return_value.json.return_value = {"success": True, "action": "other"}
    with pytest.raises(ValidationError) as exc:
        TurnstileField(action="login").clean("tok")
    assert exc.value.code == "captcha_invalid"

    mock_post.return_value.json.return_value = {"success": True, "action": "login"}
    assert TurnstileField(action="login").clean("tok") == "tok"


def test_required_message_and_custom_error_messages():
    field = TurnstileField(error_messages={"required": "solve it"})
    with pytest.raises(ValidationError, match="solve it"):
        field.clean("")
    with pytest.raises(ValidationError, match="Turnstile challenge"):
        TurnstileField().clean("")
