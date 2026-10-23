import uuid

from django.db import models
from django.db.models.functions import Lower

from domain.karaoke.entities import FULLNAME_MAX_LENGTH, PSEUDO_MAX_LENGTH


class ParticipantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=FULLNAME_MAX_LENGTH)
    pseudo = models.CharField(max_length=PSEUDO_MAX_LENGTH)
    created_at = models.DateTimeField()

    class Meta:
        constraints = [models.UniqueConstraint(Lower("pseudo"), name="unique_pseudo_ci")]

    def __str__(self) -> str:
        return self.pseudo


class RecoveryCodeModel(models.Model):
    participant = models.OneToOneField(
        ParticipantModel, on_delete=models.CASCADE, related_name="recovery_code"
    )
    code_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField()
    rotated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"recovery code of {self.participant_id}"
