"""Prove the shared test tooling works before features depend on it.

Covers the factory defaults, the `member` fixtures, and pytest-django's rule
that database access needs the `db` fixture (or the `django_db` mark).
"""

import pytest
from django.contrib.auth import get_user_model
from factories import UserFactory

User = get_user_model()


def test_user_factory_saves_a_row(db) -> None:
    UserFactory()

    assert User.objects.count() == 1


def test_user_factory_overrides_win_over_defaults(db) -> None:
    user = UserFactory(username="alice")

    assert user.username == "alice"
    assert user.email == "alice@example.test"


def test_user_factory_gives_each_user_a_unique_username(db) -> None:
    first, second = UserFactory(), UserFactory()

    assert first.username != second.username


def test_member_fixture_is_saved_and_not_staff(member) -> None:
    assert User.objects.filter(pk=member.pk).exists()
    assert member.is_staff is False


def test_member_client_is_logged_in_as_member(member_client, member) -> None:
    assert member_client.session["_auth_user_id"] == str(member.pk)


def test_database_access_without_db_fixture_is_blocked() -> None:
    """Without `db`, pytest-django refuses queries. Read this error when it fails."""
    with pytest.raises(RuntimeError, match="Database access not allowed"):
        UserFactory()
