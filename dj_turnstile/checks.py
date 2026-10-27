from django.core.checks import Error, Warning, register

from . import conf


@register()
def turnstile_settings_check(app_configs, **kwargs):
    messages = []
    missing = conf.keys_missing()
    if conf.is_testing():
        messages.append(
            Warning(
                "TURNSTILE_TESTING is enabled: unset keys fall back to Cloudflare's "
                "dummy test keys and every challenge will pass.",
                hint=(
                    "Disable TURNSTILE_TESTING in production, or add "
                    "'dj_turnstile.turnstile_test_key_error' to "
                    "SILENCED_SYSTEM_CHECKS."
                ),
                id="dj_turnstile.turnstile_test_key_error",
            )
        )
    elif missing:
        messages.append(
            Error(
                f"{' and '.join(missing)} not set.",
                hint="Set your Cloudflare Turnstile keys, or TURNSTILE_TESTING = True.",
                id="dj_turnstile.turnstile_keys_missing",
            )
        )
    return messages
