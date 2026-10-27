# dj-turnstile

A reusable Django app that integrates [Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/) into Django forms. Drop in a form field and widget, server-side verification is handled automatically. I wrote this for myself so I don't have to keep reimplimenting this at work.

## Requirements

- Python 3.10+
- Django 5.2+ (tested against 5.2 LTS, 6.0 and 6.1)

## Installation

```bash
uv add dj-turnstile
# or
pip install dj-turnstile
```

To install unreleased changes straight from GitHub:

```bash
uv add git+https://github.com/laffchem/dj-turnstile.git
```

## Setup

### 1. Get your Turnstile keys

Go to the [Cloudflare Turnstile dashboard](https://dash.cloudflare.com/) and create a new site to obtain your **Site Key** and **Secret Key**.

### 2. Add your keys to Django settings

```python
# settings.py
TURNSTILE_SITEKEY = "your-site-key"
TURNSTILE_SECRET  = "your-secret-key"
```

Add the app so its template and system check are discovered:

```python
INSTALLED_APPS = [..., "dj_turnstile"]
```

Both keys are required: if either is unset, the field and widget raise `ImproperlyConfigured` and a system check reports an error.

For local development and tests you can opt in to Cloudflare's [dummy test keys](https://developers.cloudflare.com/turnstile/troubleshooting/testing/) (every challenge passes):

```python
TURNSTILE_TESTING = True  # default False; real keys, if set, still take precedence
```

While `TURNSTILE_TESTING` is on, a system check warns (`dj_turnstile.turnstile_test_key_error`, silenceable via `SILENCED_SYSTEM_CHECKS`). Keep it off in production.

### Optional settings

| Setting                            | Default                                                  | Purpose                              |
| ---------------------------------- | -------------------------------------------------------- | ------------------------------------ |
| `TURNSTILE_VERIFY_REQUEST_TIMEOUT` | `5`                                                      | siteverify timeout (seconds)         |
| `TURNSTILE_PROXIES`                | `None`                                                   | `proxies` mapping passed to niquests |
| `TURNSTILE_VERIFY_URL`             | `https://challenges.cloudflare.com/turnstile/v0/siteverify` | Override the verify endpoint         |
| `TURNSTILE_API_URL`                | `https://challenges.cloudflare.com/turnstile/v0/api.js`  | Override the script URL              |

## Usage

Add `TurnstileField` to any Django form:

```python
from django import forms
from dj_turnstile.fields import TurnstileField

class ContactForm(forms.Form):
    name    = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = TurnstileField()
```

Render the form normally in your template:

```html
<form method="post">
	{% csrf_token %} {{ form.as_p }}
	<button type="submit">Send</button>
</form>
```

When the form is submitted, `TurnstileField.clean()` automatically posts the user's token to Cloudflare's verification endpoint and raises a `ValidationError` on failure — no extra code needed in your view.

## Field and widget options

```python
captcha = TurnstileField(
    action="login",            # checked against the action Cloudflare returns
    cdata="session-id",        # customer data echoed back by Cloudflare
    public_key="...",          # override TURNSTILE_SITEKEY for this field
    private_key="...",         # override TURNSTILE_SECRET for this field
    error_messages={"captcha_invalid": "Try again"},
    widget=TurnstileWidget(
        theme="dark", size="compact", appearance="interaction-only",
        language="de", api_params={"render": "explicit"},
    ),
)
```

Error codes: `required`, `captcha_invalid` (bad/expired token or action mismatch), and `captcha_error` (Cloudflare unreachable or rejected our request/secret).

### Forwarding the client IP

The field does not inspect the request. Pass the IP from your view through the form:

```python
class ContactForm(forms.Form):
    captcha = TurnstileField()

    def __init__(self, *args, remote_ip=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["captcha"].remote_ip = remote_ip
```

### Signal

`dj_turnstile.signals.turnstile_validation_complete` is sent after each siteverify call with `response_data` (decoded JSON) and `remote_ip`.

### Multiple widgets

`api.js` is injected once per page even when several widgets are rendered.

## How it works

| Component         | Responsibility                                                                          |
| ----------------- | --------------------------------------------------------------------------------------- |
| `TurnstileWidget` | Renders the `<div class="cf-turnstile">` element and loads the Cloudflare JS            |
| `TurnstileField`  | Reads the `cf-turnstile-response` POST value and verifies it against the Cloudflare API |

The field POSTs to `https://challenges.cloudflare.com/turnstile/v0/siteverify` using [niquests](https://github.com/jawah/niquests) with a configurable timeout (5 seconds by default). Network errors surface as a user-friendly `ValidationError` rather than an unhandled exception.

## Running the tests

Tests use [pytest](https://docs.pytest.org/) and [pytest-django](https://pytest-django.readthedocs.io/):

```bash
uv run --group dev pytest
```

To run the full suite against every supported Django version (5.2, 6.0 and 6.1), use [tox](https://tox.wiki/):

```bash
uv tool install tox --with tox-uv
tox
```

CI runs this same matrix on every push and pull request via [.github/workflows/tests.yml](.github/workflows/tests.yml).

## License

MIT [LICENSE](LICENSE).
