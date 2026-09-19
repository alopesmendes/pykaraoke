"""Prove the project boots before anything else is tested.

These do not touch a database, a view, or a model — they exist to catch a
broken settings.py (a bad env var, a missing dependency, a misconfigured
security setting) before that failure shows up as a confusing error in an
unrelated test.
"""

from django.conf import settings
from django.core.management import call_command


def test_settings_module_loads_with_the_expected_values() -> None:
    assert settings.DEBUG is False
    assert "django.contrib.admin" in settings.INSTALLED_APPS
    assert settings.DATABASES["default"]["ENGINE"]


def test_system_check_passes() -> None:
    """`manage.py check` — the same check that fails loudly on a broken import."""
    call_command("check")


def test_deploy_security_check_passes_with_no_warnings() -> None:
    """`manage.py check --deploy --tag security`, but --fail-level=WARNING
    actually fails the test if a warning appears, instead of only failing on
    hard errors.

    Scoped to the "security" tag on purpose: this is the same command chunk 2
    proved goes from 6 warnings (DEBUG=True, weak key) to 0 (DEBUG=False, real
    key, real ALLOWED_HOSTS) with no code change. The unscoped --deploy check
    also runs a "mail" check that Django's own test framework cannot pass —
    pytest-django always swaps MAILERS to the locmem backend so tests can
    inspect mail.outbox, and --deploy correctly flags locmem as a dev-only
    backend. That failure is the test framework working as intended, not a
    real deployment problem, so it is out of scope here.
    """
    call_command("check", deploy=True, tags=["security"], fail_level="WARNING")
