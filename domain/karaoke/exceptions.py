class KaraokeError(Exception):
    """Base for every domain error, so callers can catch them all at once."""


class InvalidParticipantData(KaraokeError):
    """A participant field breaks a business rule (length)."""


class PseudoTaken(KaraokeError):
    """Another participant already uses this pseudo."""


class InvalidCredentials(KaraokeError):
    """Pseudo or recovery code is wrong. Never says which."""


class RecoveryCodeNotFound(KaraokeError):
    """No recovery code exists for this participant."""


class NotAdmin(KaraokeError):
    """The caller is not allowed to reset a recovery code."""
