from skyweave.advisories import shift_flight,suggest_delays

def test_shift(crossing_flights):
    f=crossing_flights[0]
    moved=shift_flight(f,60)
    assert moved.fixes[0].t==60 and moved.fixes[0].lat==f.fixes[0].lat

def test_ranked(crossing_flights):
    results=suggest_delays(crossing_flights)
    assert len(results)==16
    assert results==sorted(results,key=lambda r:(-r['improvement'],r['delay_s'],r['callsign']))

def test_no_conflict_baseline(separated_flights):
    assert all(x['conflicts_before']==0 for x in suggest_delays(separated_flights))
