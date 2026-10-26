from dataclasses import dataclass, field

import niquests

from . import conf


@dataclass
class TurnstileResponse:
    is_valid: bool
    error_codes: list = field(default_factory=list)
    extra_data: dict = field(default_factory=dict)


def submit(token, secret, remoteip=None, idempotency_key=None):
    """
    POST a Turnstile token to siteverify and return a TurnstileResponse.

    Network failures raise niquests.exceptions.RequestException; the caller
    decides how to surface them.
    """
    data = {"secret": secret, "response": token}
    if remoteip:
        data["remoteip"] = remoteip
    if idempotency_key:
        data["idempotency_key"] = idempotency_key

    with niquests.Session() as session:
        response = session.post(
            conf.get_verify_url(),
            data=data,
            timeout=conf.get_timeout(),
            proxies=conf.get_proxies(),
        )
        result = response.json()

    return TurnstileResponse(
        is_valid=bool(result.get("success")),
        error_codes=result.get("error-codes", []),
        extra_data=result,
    )
