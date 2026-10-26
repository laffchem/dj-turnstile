from django_cf_turnstile import client


def test_submit_sends_optional_params_and_settings(settings, mock_post):
    settings.TURNSTILE_VERIFY_URL = "https://proxy.example/siteverify"
    settings.TURNSTILE_VERIFY_REQUEST_TIMEOUT = 2
    settings.TURNSTILE_PROXIES = {"https": "http://p:8080"}
    mock_post.return_value.json.return_value = {"success": True, "hostname": "x"}

    resp = client.submit("tok", "sec", remoteip="1.2.3.4", idempotency_key="abc")

    assert resp.is_valid
    assert resp.extra_data["hostname"] == "x"
    args, kwargs = mock_post.call_args
    assert args[0] == "https://proxy.example/siteverify"
    assert kwargs["data"] == {
        "secret": "sec",
        "response": "tok",
        "remoteip": "1.2.3.4",
        "idempotency_key": "abc",
    }
    assert kwargs["timeout"] == 2
    assert kwargs["proxies"] == {"https": "http://p:8080"}


def test_submit_omits_unset_params(mock_post):
    mock_post.return_value.json.return_value = {
        "success": False,
        "error-codes": ["invalid-input-response"],
    }
    resp = client.submit("tok", "sec")
    assert not resp.is_valid
    assert resp.error_codes == ["invalid-input-response"]
    assert mock_post.call_args.kwargs["data"] == {"secret": "sec", "response": "tok"}
