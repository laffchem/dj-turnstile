from django.utils.translation import gettext_lazy as _

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
API_URL = "https://challenges.cloudflare.com/turnstile/v0/api.js"
RESPONSE_FIELD_NAME = "cf-turnstile-response"
DEFAULT_TIMEOUT = 5

# Cloudflare's documented dummy keys: https://developers.cloudflare.com/turnstile/troubleshooting/testing/
TEST_SITEKEY = "1x00000000000000000000AA"
TEST_SECRET = "1x0000000000000000000000000000000AA"

# Cloudflare siteverify error codes that mean the token itself was rejected,
# as opposed to a problem with our request or configuration.
TOKEN_ERROR_CODES = {
    "missing-input-response",
    "invalid-input-response",
    "timeout-or-duplicate",
}

DEFAULT_ERROR_MESSAGES = {
    "required": _("Please complete the Turnstile challenge."),
    "captcha_invalid": _("Turnstile verification failed. Please try again."),
    "captcha_error": _("Verification service is currently unavailable"),
}
