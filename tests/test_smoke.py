"""Prove the project boots before anything else is tested.

No database, view, or model here. These catch a broken settings.py before
that failure shows up as a confusing error in an unrelated test.
"""

from django.conf import settings
from django.core.management import call_command


def test_settings_module_loads_with_the_expected_values() -> None:
    assert settings.DEBUG is False
    assert "django.contrib.admin" in settings.INSTALLED_APPS
    assert settings.DATABASES["default"]["ENGINE"]


def test_system_check_passes() -> None:
    """`manage.py check`: the same check that fails loudly on a broken import."""
    call_command("check")


def test_deploy_security_check_passes_with_no_warnings() -> None:
    """--fail-level=WARNING fails the test on any warning, not just hard errors.

    Scoped to "security" on purpose: pytest-django always swaps MAILERS to
    locmem so tests can read mail.outbox, and the unscoped --deploy check
    would then always fail on "mail" for that reason alone. Not a real
    deployment problem, so it stays out of scope here.
    """
    call_command("check", deploy=True, tags=["security"], fail_level="WARNING")
