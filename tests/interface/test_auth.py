import hashlib

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from domain.karaoke.entities import FULLNAME_MAX_LENGTH, PSEUDO_MAX_LENGTH
from infrastructure.db.karaoke.models import RecoveryCodeModel

pytestmark = pytest.mark.django_db

SIGN_UP = {"fullname": "Marie Curie", "pseudo": "marie"}


@pytest.fixture
def api():
    return APIClient()


def post(api, name, payload):
    return api.post(reverse(name), payload, format="json", secure=True)


def test_sign_up_returns_a_recovery_code_and_tokens(api):
    response = post(api, "auth-sign-up", SIGN_UP)

    body = response.json()
    assert response.status_code == 201
    assert len(body["recovery_code"]) >= 22
    assert body["access_token"]
    assert body["refresh_token"]
    assert response["Cache-Control"] == "no-store"


def test_sign_up_response_never_contains_the_fullname(api):
    response = post(api, "auth-sign-up", SIGN_UP)

    assert "Marie Curie" not in response.content.decode()


def test_sign_up_stores_only_the_sha256_of_the_code(api):
    code = post(api, "auth-sign-up", SIGN_UP).json()["recovery_code"]

    stored = RecoveryCodeModel.objects.get().code_hash

    assert stored == hashlib.sha256(code.encode()).hexdigest()
    assert stored != code


@pytest.mark.parametrize(
    "payload",
    [
        {"fullname": "a" * (FULLNAME_MAX_LENGTH + 1), "pseudo": "marie"},
        {"fullname": "Marie Curie", "pseudo": "a" * (PSEUDO_MAX_LENGTH + 1)},
        {"fullname": "Marie Curie"},
        {"fullname": "  ", "pseudo": "marie"},
    ],
)
def test_sign_up_rejects_invalid_input(api, payload):
    assert post(api, "auth-sign-up", payload).status_code == 400


def test_sign_up_rejects_a_pseudo_differing_only_by_case(api):
    post(api, "auth-sign-up", {"fullname": "Marie Curie", "pseudo": "Marie"})

    response = post(api, "auth-sign-up", {"fullname": "Other", "pseudo": "marie"})

    assert response.status_code == 409


def test_sign_in_with_the_right_code_returns_tokens(api):
    code = post(api, "auth-sign-up", SIGN_UP).json()["recovery_code"]

    response = post(api, "auth-sign-in", {"pseudo": "Marie", "recovery_code": code})

    assert response.status_code == 200
    assert response.json().keys() == {"access_token", "refresh_token"}


def test_unknown_pseudo_and_wrong_code_get_the_same_answer(api):
    post(api, "auth-sign-up", SIGN_UP)

    wrong_code = post(api, "auth-sign-in", {"pseudo": "marie", "recovery_code": "wrong"})
    unknown = post(api, "auth-sign-in", {"pseudo": "nobody", "recovery_code": "wrong"})

    assert wrong_code.status_code == unknown.status_code == 401
    assert wrong_code.json() == unknown.json()
