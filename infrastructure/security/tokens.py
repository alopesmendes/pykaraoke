import uuid

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from application.karaoke.interfaces import TokenIssuer, TokenPair


class SimpleJwtTokenIssuer(TokenIssuer):
    @classmethod
    def issue(cls, participant_id: uuid.UUID) -> TokenPair:
        user = get_user_model().objects.get(username=str(participant_id))
        refresh = RefreshToken.for_user(user)
        return TokenPair(access_token=str(refresh.access_token), refresh_token=str(refresh))

    @classmethod
    def revoke_all(cls, participant_id: uuid.UUID) -> None:
        outstanding = OutstandingToken.objects.filter(user__username=str(participant_id))
        for token in outstanding:
            BlacklistedToken.objects.get_or_create(token=token)
