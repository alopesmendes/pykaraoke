import uuid
from dataclasses import dataclass
from datetime import datetime

from domain.karaoke.exceptions import InvalidParticipantData

FULLNAME_MAX_LENGTH = 120
PSEUDO_MAX_LENGTH = 60


@dataclass(frozen=True)
class Participant:
    id: uuid.UUID
    fullname: str
    pseudo: str
    created_at: datetime

    def __post_init__(self) -> None:
        if len(self.fullname) > FULLNAME_MAX_LENGTH:
            raise InvalidParticipantData("fullname is too long")
        if len(self.pseudo) > PSEUDO_MAX_LENGTH:
            raise InvalidParticipantData("pseudo is too long")


@dataclass(frozen=True)
class Admin:
    id: uuid.UUID
    is_staff: bool
    fullname: str
    created_at: datetime


@dataclass(frozen=True)
class RecoveryCode:
    participant_id: uuid.UUID
    code_hash: str
    created_at: datetime
    rotated_at: datetime | None
