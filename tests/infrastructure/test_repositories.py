import uuid
from datetime import UTC, datetime

import pytest

from domain.karaoke.entities import Participant, RecoveryCode
from domain.karaoke.exceptions import PseudoTaken
from infrastructure.db.karaoke.models import ParticipantModel, RecoveryCodeModel
from infrastructure.db.karaoke.repositories import DjangoParticipantRepository

pytestmark = pytest.mark.django_db


def make_pair(pseudo, code_hash="a" * 64):
    now = datetime.now(UTC)
    participant = Participant(
        id=uuid.uuid4(), fullname="Marie Curie", pseudo=pseudo, created_at=now
    )
    code = RecoveryCode(
        participant_id=participant.id, code_hash=code_hash, created_at=now, rotated_at=None
    )
    return participant, code


def test_add_then_find_ignores_the_case_of_the_pseudo():
    repo = DjangoParticipantRepository()
    participant, code = make_pair("Marie")
    repo.add_with_recovery_code(participant, code)

    found = repo.find_by_pseudo("marie")

    assert found == (participant, code)


def test_find_returns_none_for_an_unknown_pseudo():
    assert DjangoParticipantRepository().find_by_pseudo("marie") is None


def test_duplicate_pseudo_raises_pseudo_taken_and_saves_nothing():
    repo = DjangoParticipantRepository()
    repo.add_with_recovery_code(*make_pair("Marie"))

    with pytest.raises(PseudoTaken):
        repo.add_with_recovery_code(*make_pair("Marie"))

    assert ParticipantModel.objects.count() == 1
    assert RecoveryCodeModel.objects.count() == 1


def test_replace_recovery_code_updates_the_same_row():
    repo = DjangoParticipantRepository()
    participant, code = make_pair("marie")
    repo.add_with_recovery_code(participant, code)

    new_code = RecoveryCode(
        participant_id=code.participant_id,
        code_hash="b" * 64,
        created_at=code.created_at,
        rotated_at=datetime.now(UTC),
    )
    repo.replace_recovery_code(new_code)
    assert RecoveryCodeModel.objects.count() == 1
    assert repo.find_by_pseudo("marie") == (participant, new_code)
