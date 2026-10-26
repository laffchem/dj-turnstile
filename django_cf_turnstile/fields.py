import niquests
from django.forms import Field, ValidationError

from . import client, conf
from .constants import DEFAULT_ERROR_MESSAGES, TOKEN_ERROR_CODES
from .signals import turnstile_validation_complete
from .widgets import TurnstileWidget


class TurnstileField(Field):
    widget = TurnstileWidget
    default_error_messages = DEFAULT_ERROR_MESSAGES

    def __init__(
        self,
        action=None,
        cdata=None,
        *args,
        public_key=None,
        private_key=None,
        remote_ip=None,
        **kwargs,
    ):
        widget = kwargs.get("widget") or self.widget
        if isinstance(widget, type):
            kwargs["widget"] = widget(action=action, cdata=cdata, sitekey=public_key)
        elif public_key and getattr(widget, "sitekey", None) is None:
            widget.sitekey = public_key
        kwargs.setdefault("required", True)
        super().__init__(*args, **kwargs)
        self.action = action
        self.cdata = cdata
        self.public_key = public_key
        self.private_key = private_key
        # Set by the form (e.g. in __init__) to forward the client IP to Cloudflare.
        self.remote_ip = remote_ip

    def clean(self, value):
        value = super().clean(value)

        if not value:
            return value

        secret = self.private_key or conf.get_secret()

        try:
            response = client.submit(value, secret, remoteip=self.remote_ip)
        except niquests.exceptions.RequestException:
            raise ValidationError(
                self.error_messages["captcha_error"], code="captcha_error"
            )

        turnstile_validation_complete.send(
            sender=self.__class__,
            response_data=response.extra_data,
            remote_ip=self.remote_ip,
        )

        if not response.is_valid:
            if response.error_codes and not (
                set(response.error_codes) & TOKEN_ERROR_CODES
            ):
                # Bad secret, malformed request, Cloudflare internal error, ...
                raise ValidationError(
                    self.error_messages["captcha_error"], code="captcha_error"
                )
            raise ValidationError(
                self.error_messages["captcha_invalid"], code="captcha_invalid"
            )

        if self.action and response.extra_data.get("action") != self.action:
            raise ValidationError(
                self.error_messages["captcha_invalid"], code="captcha_invalid"
            )

        return value
