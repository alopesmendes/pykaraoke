import uuid
from abc import ABC, abstractclassmethod
from dataclasses import dataclass

from domain.karaoke.entities import Participant, RecoveryCode


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


class ParticipantRepository(ABC):
    @abstractclassmethod
    def add_with_recovery_code(cls, participant: Participant, recovery_code: RecoveryCode) -> None:
        """Save both or neither. Raise PseudoTaken if the pseudo exists, whatever its case."""


class RecoveryCodeHasher(ABC):
    @abstractclassmethod
    def hash(cls, code: str) -> str:
        """Return the hex SHA-256 of the code."""


class TokenIssuer(ABC):
    @abstractclassmethod
    def issue(cls, participant_id: uuid.UUID) -> TokenPair:
        """Create an access and refresh token for this participant."""
