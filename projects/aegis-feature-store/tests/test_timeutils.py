from datetime import timezone

import pytest

from aegis_feature_store.timeutils import parse_utc, utc_text


def test_offset_normalization():
    assert utc_text("2026-01-01T14:00:00+02:00") == (
        "2026-01-01T12:00:00.000000+00:00"
    )


def test_z_is_utc():
    assert parse_utc("2026-01-01T12:00:00Z").tzinfo == timezone.utc


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError, match="timezone"):
        parse_utc("2026-01-01T12:00:00")
