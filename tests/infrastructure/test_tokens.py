import uuid
from datetime import timedelta

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from infrastructure.security.tokens import SimpleJwtTokenIssuer

pytestmark = pytest.mark.django_db


def new_participant_id():
    participant_id = uuid.uuid4()
    get_user_model().objects.create_user(username=str(participant_id))
    return participant_id


@pytest.fixture
def participant_id():
    return new_participant_id()


def test_claims_hold_a_uuid_subject_and_no_personal_data(participant_id):
    pair = SimpleJwtTokenIssuer().issue(participant_id)

    payload = AccessToken(pair.access_token).payload
    assert payload["sub"] == str(participant_id)
    assert payload["iss"] == settings.SIMPLE_JWT["ISSUER"]
    assert payload["aud"] == settings.SIMPLE_JWT["AUDIENCE"]
    assert payload["typ"] == "access"
    assert set(payload) == {"sub", "iss", "aud", "typ", "exp", "iat", "jti"}


def test_access_lifetime_is_between_5_and_15_minutes():
    lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

    assert timedelta(minutes=5) <= lifetime <= timedelta(minutes=15)


def test_refresh_rotates_and_blacklists_the_old_token(participant_id):
    old = SimpleJwtTokenIssuer().issue(participant_id).refresh_token
    serializer = TokenRefreshSerializer(data={"refresh": old})

    serializer.is_valid(raise_exception=True)

    assert serializer.validated_data["refresh"] != old
    with pytest.raises(TokenError):
        RefreshToken(old)


def test_issued_refresh_token_is_stored_as_outstanding(participant_id):
    SimpleJwtTokenIssuer().issue(participant_id)

    assert OutstandingToken.objects.filter(user__username=str(participant_id)).count() == 1


def test_tokens_are_signed_with_the_jwt_key_not_the_django_secret_key(participant_id):
    token = SimpleJwtTokenIssuer().issue(participant_id).access_token
    options = {"algorithms": ["HS256"], "audience": settings.SIMPLE_JWT["AUDIENCE"]}

    jwt.decode(token, settings.JWT_SIGNING_KEY, **options)
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, settings.SECRET_KEY, **options)


def test_a_token_with_algorithm_none_is_rejected(participant_id):
    forged = jwt.encode({"sub": str(participant_id), "Bearer": "access"}, None, algorithm="none")

    with pytest.raises(TokenError):
        AccessToken(forged)


def test_revoke_all_blacklists_every_refresh_token_of_the_participant(participant_id):
    issuer = SimpleJwtTokenIssuer()
    tokens = [issuer.issue(participant_id).refresh_token for _ in range(2)]

    issuer.revoke_all(participant_id)

    assert BlacklistedToken.objects.count() == 2
    for token in tokens:
        with pytest.raises(TokenError):
            RefreshToken(token)


def test_revoke_all_leaves_other_participants_alone(participant_id):
    issuer = SimpleJwtTokenIssuer()
    other_token = issuer.issue(new_participant_id()).refresh_token
    issuer.issue(participant_id)

    issuer.revoke_all(participant_id)

    RefreshToken(other_token)
