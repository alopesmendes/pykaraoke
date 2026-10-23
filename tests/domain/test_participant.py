import uuid
from datetime import datetime

import pytest

from domain.karaoke.entities import FULLNAME_MAX_LENGTH, PSEUDO_MAX_LENGTH, Participant
from domain.karaoke.exceptions import InvalidParticipantData


def test_fullname_at_limit_is_accepted():
    Participant(
        id=uuid.uuid4(),
        fullname="a" * FULLNAME_MAX_LENGTH,
        pseudo="marie",
        created_at=datetime.now(),
    )


def test_fullname_over_limit_is_rejected():
    with pytest.raises(InvalidParticipantData):
        Participant(
            id=uuid.uuid4(),
            fullname="a" * (FULLNAME_MAX_LENGTH + 1),
            pseudo="marie",
            created_at=datetime.now(),
        )


def test_pseudo_at_limit_is_accepted():
    Participant(
        id=uuid.uuid4(),
        fullname="Marie Curie",
        pseudo="a" * PSEUDO_MAX_LENGTH,
        created_at=datetime.now(),
    )


def test_pseudo_over_limit_is_rejected():
    with pytest.raises(InvalidParticipantData):
        Participant(
            id=uuid.uuid4(),
            fullname="Marie Curie",
            pseudo="a" * (PSEUDO_MAX_LENGTH + 1),
            created_at=datetime.now(),
        )
