import uuid
from datetime import UTC, datetime

import pytest
from django.db import IntegrityError, transaction

from infrastructure.db.karaoke.models import ParticipantModel, RecoveryCodeModel

pytestmark = pytest.mark.django_db


def make_participant(pseudo):
    return ParticipantModel.objects.create(
        id=uuid.uuid4(), fullname="Marie Curie", pseudo=pseudo, created_at=datetime.now(UTC)
    )


def make_recovery_code(participant: ParticipantModel, code_hash: str):
    return RecoveryCodeModel.objects.create(
        participant=participant,
        code_hash=code_hash,
        created_at=datetime.now(UTC),
    )


def test_pseudo_differing_only_by_case_violates_the_constraint():
    make_participant("Marie")

    with pytest.raises(IntegrityError), transaction.atomic():
        make_participant("marie")


def test_a_participant_has_at_most_one_recovery_code_row():
    participant = make_participant("Marie")
    make_recovery_code(participant=participant, code_hash="a" * 64)

    with pytest.raises(IntegrityError), transaction.atomic():
        make_recovery_code(participant=participant, code_hash="b" * 64)
