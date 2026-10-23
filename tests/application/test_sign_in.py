import hmac

import pytest

from application.karaoke import services
from application.karaoke.services import sign_in, sign_up
from domain.karaoke.exceptions import InvalidCredentials


def test_sign_in_returns_tokens_for_the_right_code(participants, hasher, issuer):
    signed_up = sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")

    tokens = sign_in(
        participants, hasher, issuer, pseudo="marie", recovery_code=signed_up.recovery_code
    )

    assert tokens == issuer.issue(signed_up.participant.id)


def test_sign_in_matches_the_pseudo_case_insensitively(participants, hasher, issuer):
    signed_up = sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="Marie")

    tokens = sign_in(
        participants, hasher, issuer, pseudo="marie", recovery_code=signed_up.recovery_code
    )

    assert tokens == issuer.issue(signed_up.participant.id)


def test_unknown_pseudo_and_wrong_code_raise_the_same_error(participants, hasher, issuer):
    sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")

    with pytest.raises(InvalidCredentials) as wrong_code:
        sign_in(participants, hasher, issuer, pseudo="marie", recovery_code="wrong")
    with pytest.raises(InvalidCredentials) as unknown_pseudo:
        sign_in(participants, hasher, issuer, pseudo="nobody", recovery_code="wrong")

    assert str(wrong_code.value) == str(unknown_pseudo.value)


@pytest.mark.parametrize("pseudo", ["marie", "nobody"])
def test_sign_in_compares_hashes_in_constant_time(
    monkeypatch, participants, hasher, issuer, pseudo
):
    sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")
    calls = []
    real_compare = hmac.compare_digest

    def spy(a, b):
        calls.append((a, b))
        return real_compare(a, b)

    monkeypatch.setattr(services.hmac, "compare_digest", spy)

    with pytest.raises(InvalidCredentials):
        sign_in(participants, hasher, issuer, pseudo=pseudo, recovery_code="wrong")

    assert len(calls) == 1
