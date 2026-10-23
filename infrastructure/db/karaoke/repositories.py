from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.functions import Lower

from application.karaoke.interfaces import ParticipantRepository
from domain.karaoke.entities import Participant, RecoveryCode
from domain.karaoke.exceptions import PseudoTaken
from infrastructure.db.karaoke.models import ParticipantModel, RecoveryCodeModel


class DjangoParticipantRepository(ParticipantRepository):
    @classmethod
    def add_with_recovery_code(cls, participant: Participant, recovery_code: RecoveryCode) -> None:
        try:
            with transaction.atomic():
                get_user_model().objects.create_user(username=str(participant.id))

                ParticipantModel.objects.create(
                    id=participant.id,
                    fullname=participant.fullname,
                    pseudo=participant.pseudo,
                    created_at=participant.created_at,
                )
                RecoveryCodeModel.objects.create(
                    participant_id=participant.id,
                    code_hash=recovery_code.code_hash,
                    created_at=recovery_code.created_at,
                    rotated_at=recovery_code.rotated_at,
                )
        except IntegrityError as exc:
            if "unique_pseudo_ci" not in str(exc):
                raise
            raise PseudoTaken(participant.pseudo) from exc

    @classmethod
    def find_by_pseudo(cls, pseudo: str) -> tuple[Participant, RecoveryCode] | None:
        row = (
            RecoveryCodeModel.objects.select_related("participant")
            .alias(pseudo_lower=Lower("participant__pseudo"))
            .filter(pseudo_lower=pseudo.lower())
            .first()
        )
        if row is None:
            return None
        person = row.participant
        return (
            Participant(
                id=person.id,
                fullname=person.fullname,
                pseudo=person.pseudo,
                created_at=person.created_at,
            ),
            RecoveryCode(
                participant_id=person.id,
                code_hash=row.code_hash,
                created_at=row.created_at,
                rotated_at=row.rotated_at,
            ),
        )

    @classmethod
    def replace_recovery_code(cls, recovery_code: RecoveryCode) -> None:
        RecoveryCodeModel.objects.filter(participant_id=recovery_code.participant_id).update(
            code_hash=recovery_code.code_hash,
            created_at=recovery_code.created_at,
            rotated_at=recovery_code.rotated_at,
        )
