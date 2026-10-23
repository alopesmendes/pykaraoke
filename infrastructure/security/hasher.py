import hashlib

from application.karaoke.interfaces import RecoveryCodeHasher


class Sha256RecoveryCodeHasher(RecoveryCodeHasher):
    @classmethod
    def hash(cls, code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()
