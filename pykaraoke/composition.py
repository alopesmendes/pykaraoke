from application.karaoke import services
from application.karaoke.interfaces import TokenPair
from infrastructure.db.karaoke.repositories import DjangoParticipantRepository
from infrastructure.security.hasher import Sha256RecoveryCodeHasher
from infrastructure.security.tokens import SimpleJwtTokenIssuer


def sign_up(*, fullname: str, pseudo: str) -> services.SignUpResult:
    return services.sign_up(
        DjangoParticipantRepository(),
        Sha256RecoveryCodeHasher(),
        SimpleJwtTokenIssuer(),
        fullname=fullname,
        pseudo=pseudo,
    )


def sign_in(*, pseudo: str, recovery_code: str) -> TokenPair:
    return services.sign_in(
        DjangoParticipantRepository(),
        Sha256RecoveryCodeHasher(),
        SimpleJwtTokenIssuer(),
        pseudo=pseudo,
        recovery_code=recovery_code,
    )
