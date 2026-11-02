class VaultlineError(Exception):
    """Expected validation, integrity, or storage failure."""

class IntegrityError(VaultlineError):
    """An object or manifest did not match its digest."""
