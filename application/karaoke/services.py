import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from application.karaoke.interfaces import (
    ParticipantRepository,
    RecoveryCodeHasher,
    TokenIssuer,
    TokenPair,
)
from domain.karaoke.entities import Participant, RecoveryCode

RECOVERY_CODE_BYTES = 16  # 128 bits


@dataclass(frozen=True)
class SignUpResult:
    participant: Participant
    recovery_code: str
    tokens: TokenPair


def sign_up(
    participants: ParticipantRepository,
    hasher: RecoveryCodeHasher,
    issuer: TokenIssuer,
    *,
    fullname: str,
    pseudo: str,
) -> SignUpResult:
    participant = Participant(
        id=uuid.uuid4(),
        fullname=fullname,
        pseudo=pseudo,
        created_at=datetime.now(UTC),
    )
    raw_code = secrets.token_urlsafe(RECOVERY_CODE_BYTES)
    recovery_code = RecoveryCode(
        participant_id=participant.id,
        code_hash=hasher.hash(raw_code),
        created_at=datetime.now(UTC),
        rotated_at=None,
    )

    participants.add_with_recovery_code(participant, recovery_code)
    return SignUpResult(
        participant=participant,
        recovery_code=raw_code,
        tokens=issuer.issue(participant.id),
    )
