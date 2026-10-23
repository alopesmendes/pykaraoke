from infrastructure.security.hasher import Sha256RecoveryCodeHasher


def test_hash_is_the_hex_sha256_of_the_code():
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

    assert Sha256RecoveryCodeHasher().hash("abc") == expected


def test_hash_fits_the_column_and_never_contains_the_raw_code():
    code = "some-recovery-code"

    hashed = Sha256RecoveryCodeHasher().hash(code)

    assert len(hashed) == 64
    assert code not in hashed
