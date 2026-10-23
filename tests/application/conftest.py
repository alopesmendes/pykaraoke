import uuid

import pytest

from application.karaoke.interfaces import (
    ParticipantRepository,
    RecoveryCodeHasher,
    TokenIssuer,
    TokenPair,
)
from domain.karaoke.entities import Participant, RecoveryCode
from domain.karaoke.exceptions import PseudoTaken


class FakeParticipantRepository(ParticipantRepository):
    participants: dict[str, Participant]
    codes: dict[str, RecoveryCode]

    def __init__(self):
        self.participants: dict[str, Participant] = {}
        self.codes: dict[str, RecoveryCode] = {}

    def add_with_recovery_code(self, participant: Participant, recovery_code: RecoveryCode):
        key = participant.pseudo.lower()
        if key in self.participants:
            raise PseudoTaken(participant.pseudo)
        self.participants[key] = participant
        self.codes[key] = recovery_code

    def find_by_pseudo(self, pseudo: str) -> tuple[Participant, RecoveryCode] | None:
        key = pseudo.lower()
        if key not in self.participants:
            return None
        return self.participants[key], self.codes[key]


class FakeRecoveryCodeHasher(RecoveryCodeHasher):
    @classmethod
    def hash(cls, code: str) -> str:
        return f"hashed:{code}"


class FakeTokenIssuer(TokenIssuer):
    @classmethod
    def issue(cls, participant_id: uuid.UUID) -> TokenPair:
        return TokenPair(
            access_token=f"access_token:{participant_id}",
            refresh_token=f"refresh_token:{participant_id}",
        )


@pytest.fixture
def participants():
    return FakeParticipantRepository()


@pytest.fixture
def hasher():
    return FakeRecoveryCodeHasher()


@pytest.fixture
def issuer():
    return FakeTokenIssuer()
