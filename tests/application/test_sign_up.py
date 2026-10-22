import pytest

from application.karaoke.services import sign_up
from domain.karaoke.exceptions import PseudoTaken

MIN_CODE_LENGTH = 22  # 22 base64url characters carry 132 bits


def test_sign_up_returns_recovery_code_of_at_least_128_bits(participants, hasher, issuer):
    result = sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")

    assert len(result.recovery_code) >= MIN_CODE_LENGTH


def test_sign_up_stores_the_hash_not_the_raw_code(participants, hasher, issuer):
    result = sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")

    stored = participants.codes["marie"].code_hash
    assert stored == f"hashed:{result.recovery_code}"
    assert stored != result.recovery_code


def test_sign_up_returns_tokens_for_the_new_participant(participants, hasher, issuer):
    result = sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="marie")

    assert result.tokens == issuer.issue(result.participant.id)


def test_sign_up_rejects_a_pseudo_differing_only_by_case(participants, hasher, issuer):
    sign_up(participants, hasher, issuer, fullname="Marie Curie", pseudo="Marie")

    with pytest.raises(PseudoTaken):
        sign_up(participants, hasher, issuer, fullname="Other", pseudo="marie")
