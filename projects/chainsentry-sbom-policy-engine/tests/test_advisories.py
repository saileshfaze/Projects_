import pytest
from chainsentry.advisories import load_feed, matches, purl_package, FeedError
from chainsentry.models import Component


def test_purl_normalization():
    assert purl_package("pkg:pypi/Flask@2.0?arch=x#src") == "pypi/flask"
    assert purl_package("bad") == ""


def test_affected_interval(fixture_data):
    adv = load_feed(fixture_data("advisories.json"))[0]
    assert matches(Component("a", "cipherleaf", "0.8.1", "pkg:pypi/cipherleaf@0.8.1"), adv)
    assert not matches(Component("a", "cipherleaf", "0.9.0", "pkg:pypi/cipherleaf@0.9.0"), adv)


def test_invalid_version_skips_match(fixture_data):
    adv = load_feed(fixture_data("advisories.json"))[0]
    assert not matches(Component("a", "cipherleaf", "unknown", "pkg:pypi/cipherleaf@unknown"), adv)


def test_duplicate_advisory_rejected(fixture_data):
    feed = fixture_data("advisories.json")
    feed["advisories"].append(feed["advisories"][0])
    with pytest.raises(FeedError):
        load_feed(feed)


def test_bad_interval_rejected():
    with pytest.raises(FeedError):
        load_feed({"advisories": [{"id": "X", "purl_name": "pypi/x", "introduced": "2", "fixed": "1", "severity": "high"}]})


def test_invalid_feed_rejected():
    with pytest.raises(FeedError):
        load_feed([])
