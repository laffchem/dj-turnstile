from urllib.parse import urlencode

from django.forms import Widget

from . import conf
from .constants import RESPONSE_FIELD_NAME


class TurnstileWidget(Widget):
    template_name = "dj_turnstile/turnstile.html"

    def __init__(
        self,
        action=None,
        cdata=None,
        attrs=None,
        sitekey=None,
        theme=None,
        size=None,
        appearance=None,
        language=None,
        api_params=None,
    ):
        default_attrs = {}
        for name, value in (
            ("action", action),
            ("cdata", cdata),
            ("theme", theme),
            ("size", size),
            ("appearance", appearance),
            ("language", language),
        ):
            if value:
                default_attrs[f"data-{name}"] = value
        if attrs:
            default_attrs.update(attrs)

        super().__init__(attrs=default_attrs)
        self.action = action
        self.cdata = cdata
        self.sitekey = sitekey
        # Query parameters for api.js, e.g. {"render": "explicit", "onload": "cb"}.
        self.api_params = api_params or {}

    # The challenge is injected by Cloudflare's JS, so the browser can't
    # enforce `required` on a visible input.
    def use_required_attribute(self, initial):
        return False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["action"] = self.action
        context["cdata"] = self.cdata
        context["widget"]["sitekey"] = self.sitekey or conf.get_sitekey()
        api_url = conf.get_api_url()
        if self.api_params:
            api_url = f"{api_url}?{urlencode(self.api_params)}"
        context["widget"]["api_url"] = api_url
        return context

    def value_from_datadict(self, data, files, name):
        return data.get(RESPONSE_FIELD_NAME, None)
