import hmac
import logging
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
from domain.karaoke.entities import Admin, Participant, RecoveryCode
from domain.karaoke.exceptions import InvalidCredentials, NotAdmin, RecoveryCodeNotFound

UNKNOWN_PSEUDO_HASH = "0" * 64

RECOVERY_CODE_BYTES = 16  # 128 bits
logger = logging.getLogger(__name__)


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


def sign_in(
    participants: ParticipantRepository,
    hasher: RecoveryCodeHasher,
    issuer: TokenIssuer,
    *,
    pseudo: str,
    recovery_code: str,
) -> TokenPair:
    found = participants.find_by_pseudo(pseudo)
    stored_hash = found[1].code_hash if found else UNKNOWN_PSEUDO_HASH
    code_matches = hmac.compare_digest(hasher.hash(recovery_code), stored_hash)
    if found is None or not code_matches:
        raise InvalidCredentials("invalid pseudo or recovery code")
    return issuer.issue(found[0].id)


def reset_recovery_code(
    participants: ParticipantRepository,
    hasher: RecoveryCodeHasher,
    issuer: TokenIssuer,
    *,
    admin: Admin,
    pseudo: str,
) -> str:
    if not admin.is_staff:
        raise NotAdmin("admin rights required")
    found = participants.find_by_pseudo(pseudo)
    if not found:
        raise RecoveryCodeNotFound("invalid pseudo or recovery code")

    participant, old_code = found
    raw_code = secrets.token_urlsafe(RECOVERY_CODE_BYTES)
    participants.replace_recovery_code(
        RecoveryCode(
            participant_id=participant.id,
            code_hash=hasher.hash(raw_code),
            created_at=old_code.created_at,
            rotated_at=datetime.now(UTC),
        )
    )
    issuer.revoke_all(participant.id)
    logger.info("recovery code reset by admin=%s for participant=%s", admin.id, participant.id)
    return raw_code
