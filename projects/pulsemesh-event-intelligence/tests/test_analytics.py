from pulsemesh.analytics import robust_scores, score_windows


def test_empty_series():
    assert robust_scores([]) == []


def test_constant_baseline_and_spike():
    assert robust_scores([2, 2, 2, 20])[-1] == 999.0


def test_scores_are_per_event_type():
    rows = [
        {"event_type": "click", "count": 2},
        {"event_type": "click", "count": 2},
        {"event_type": "click", "count": 30},
        {"event_type": "purchase", "count": 100},
    ]
    scored = score_windows(rows)
    assert scored[2]["anomalous"] is True
    assert scored[3]["anomalous"] is False
