from voltpilot.audit import chain,verify
from voltpilot.dispatch import simulate


def test_chain_valid(profile,site):
    _,steps=simulate(profile,site)
    assert verify(chain(steps))


def test_chain_detects_tampering(profile,site):
    _,steps=simulate(profile,site)
    entries=chain(steps)
    entries[3]["step"]["soc_kwh"]=99
    assert not verify(entries)


def test_chain_detects_reordering(profile,site):
    _,steps=simulate(profile,site)
    entries=chain(steps)
    entries[1],entries[2]=entries[2],entries[1]
    assert not verify(entries)
