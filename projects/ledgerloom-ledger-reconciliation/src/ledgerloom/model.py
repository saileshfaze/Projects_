"""Validated journal model; money is integer minor units."""
from dataclasses import dataclass
from datetime import date

class LedgerError(ValueError):
    pass

@dataclass(frozen=True)
class Posting:
    account: str
    amount: int
    def __post_init__(self):
        if not isinstance(self.account, str) or not self.account.strip():
            raise LedgerError("account is required")
        if type(self.amount) is not int or self.amount == 0:
            raise LedgerError("posting must be a nonzero integer in minor units")

@dataclass(frozen=True)
class Entry:
    key: str
    day: str
    description: str
    postings: tuple[Posting, ...]
    reference: str = ""
    def __post_init__(self):
        if not self.key or not isinstance(self.key, str):
            raise LedgerError("idempotency key required")
        try:
            date.fromisoformat(self.day)
        except (TypeError, ValueError) as exc:
            raise LedgerError("day must be ISO date") from exc
        if len(self.postings) < 2 or sum(p.amount for p in self.postings) != 0:
            raise LedgerError("journal entry must balance with at least two postings")
        if not self.description.strip():
            raise LedgerError("description required")
