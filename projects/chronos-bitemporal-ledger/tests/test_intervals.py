from datetime import date

import pytest

from chronos_ledger.intervals import overlaps, remainder, validate_interval


def d(value):
    return date.fromisoformat(value)


def test_touching_intervals_do_not_overlap():
    assert not overlaps(d("2026-01-01"), d("2026-02-01"), d("2026-02-01"), d("2026-03-01"))


def test_remainder_splits_both_sides():
    assert remainder(d("2026-01-01"), d("2027-01-01"), d("2026-03-01"), d("2026-07-01")) == [
        (d("2026-01-01"), d("2026-03-01")),
        (d("2026-07-01"), d("2027-01-01")),
    ]


def test_disjoint_remainder_unchanged():
    assert remainder(d("2026-01-01"), d("2026-02-01"), d("2026-03-01"), d("2026-04-01")) == [
        (d("2026-01-01"), d("2026-02-01"))
    ]


def test_invalid_interval_rejected():
    with pytest.raises(ValueError):
        validate_interval(d("2026-02-01"), d("2026-02-01"))
