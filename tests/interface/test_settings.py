"""Settings the hosting platform depends on.

Prod settings are what the suite runs on, so most checks read them directly.
The env-driven checks reload a settings module with a patched environment,
then reload it again afterwards so later tests see the real values.
"""

import importlib
import re

from django.conf import settings


def test_prod_trusts_the_proxy_for_https() -> None:
    """Render terminates TLS and forwards plain HTTP. Without this header,
    request.is_secure() is False and SECURE_SSL_REDIRECT loops forever."""
    assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")


def test_a_request_the_proxy_forwarded_as_https_is_not_redirected(client) -> None:
    response = client.get("/admin/login/", headers={"X-Forwarded-Proto": "https"})

    assert response.status_code == 200


def test_prod_exempts_the_health_probe_from_the_https_redirect() -> None:
    assert any(re.match(pattern, "health/") for pattern in settings.SECURE_REDIRECT_EXEMPT)


def test_csrf_trusted_origins_are_read_from_the_environment(monkeypatch) -> None:
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://a.example.com,https://b.example.com")
    base = importlib.reload(importlib.import_module("pykaraoke.settings.base"))
    try:
        assert base.CSRF_TRUSTED_ORIGINS == [
            "https://a.example.com",
            "https://b.example.com",
        ]
    finally:
        monkeypatch.undo()
        importlib.reload(base)


def test_api_docs_are_off_in_prod_by_default() -> None:
    assert settings.ENABLE_API_DOCS is False


def test_api_docs_are_on_in_dev_by_default(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_API_DOCS", raising=False)
    dev = importlib.reload(importlib.import_module("pykaraoke.settings.dev"))
    try:
        assert dev.ENABLE_API_DOCS is True
    finally:
        monkeypatch.undo()
        importlib.reload(dev)
