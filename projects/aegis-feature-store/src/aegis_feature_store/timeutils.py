"""UTC normalization used by both ingestion and historical retrieval."""

from datetime import datetime, timezone


def parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("Timestamp must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp must contain an explicit timezone")
    return parsed.astimezone(timezone.utc)


def utc_text(value: str | datetime) -> str:
    parsed = parse_utc(value) if isinstance(value, str) else value.astimezone(timezone.utc)
    return parsed.isoformat(timespec="microseconds")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
