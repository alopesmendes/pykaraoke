import logging
import uuid
from datetime import datetime

import pytest

from application.karaoke.services import reset_recovery_code, sign_in, sign_up
from domain.karaoke.entities import Admin
from domain.karaoke.exceptions import InvalidCredentials, NotAdmin, RecoveryCodeNotFound

STAFF = Admin(id=uuid.uuid4(), is_staff=True, fullname="Staff", created_at=datetime.now())
NOT_STAFF = Admin(id=uuid.uuid4(), is_staff=False, fullname="Not Staff", created_at=datetime.now())


@pytest.fixture
def marie(participants, hasher, issuer):
    return sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")


def test_reset_returns_a_new_code_and_replaces_the_hash(participants, hasher, issuer, marie):
    new_code = reset_recovery_code(participants, hasher, issuer, admin=STAFF, pseudo="marie")

    assert new_code != marie.recovery_code
    assert participants.codes["marie"].code_hash == f"hashed:{new_code}"
    assert participants.codes["marie"].rotated_at is not None


def test_old_code_stops_working_and_new_code_works(participants, hasher, issuer, marie):
    new_code = reset_recovery_code(participants, hasher, issuer, admin=STAFF, pseudo="marie")

    with pytest.raises(InvalidCredentials):
        sign_in(participants, hasher, issuer, pseudo="marie", recovery_code=marie.recovery_code)

    sign_in(participants, hasher, issuer, recovery_code=new_code, pseudo="marie")


def test_reset_revokes_the_participants_refresh_tokens(participants, hasher, issuer, marie):
    reset_recovery_code(participants, hasher, issuer, admin=STAFF, pseudo="marie")

    assert issuer.revoked == [marie.participant.id]


def test_non_admin_is_refused_and_nothing_changes(participants, hasher, issuer, marie):
    before = participants.codes["marie"]

    with pytest.raises(NotAdmin):
        reset_recovery_code(participants, hasher, issuer, admin=NOT_STAFF, pseudo="marie")

    assert participants.codes["marie"] == before
    assert issuer.revoked == []


def test_unknown_pseudo_raises_recovery_code_not_found(participants, hasher, issuer):
    with pytest.raises(RecoveryCodeNotFound):
        reset_recovery_code(participants, hasher, issuer, admin=STAFF, pseudo="unknown")


def test_reset_is_logged_without_the_code(caplog, participants, hasher, issuer, marie):
    caplog.set_level(logging.INFO)

    new_code = reset_recovery_code(participants, hasher, issuer, admin=STAFF, pseudo="marie")

    assert str(STAFF.id) in caplog.text
    assert str(marie.participant.id) in caplog.text
    assert new_code not in caplog.text
    assert "Marie Curie" not in caplog.text
