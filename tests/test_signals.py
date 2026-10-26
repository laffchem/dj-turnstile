from django_cf_turnstile.fields import TurnstileField
from django_cf_turnstile.signals import turnstile_validation_complete


def test_signal_sent_with_response_data(settings, mock_post):
    settings.TURNSTILE_SECRET = "s"
    mock_post.return_value.json.return_value = {"success": True, "hostname": "h"}
    received = []

    def receiver(sender, response_data, remote_ip, **kwargs):
        received.append((response_data, remote_ip))

    turnstile_validation_complete.connect(receiver)
    try:
        TurnstileField(remote_ip="9.9.9.9").clean("tok")
    finally:
        turnstile_validation_complete.disconnect(receiver)

    assert received == [({"success": True, "hostname": "h"}, "9.9.9.9")]
