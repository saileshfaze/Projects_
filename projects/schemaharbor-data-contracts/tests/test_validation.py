from schemaharbor.contracts import Contract
from schemaharbor.validation import validate, profile

C=Contract.from_dict({"name":"orders","version":"1","fields":[{"name":"id","kind":"integer","minimum":1},{"name":"when","kind":"date"},{"name":"memo","kind":"string","required":False}]})
def test_valid(): assert validate(C,{"id":"2","when":"2026-01-01"}) == []
def test_missing(): assert {x["code"] for x in validate(C,{})} == {"missing"}
def test_bounds(): assert validate(C,{"id":"0","when":"2026-01-01"})[0]["code"] == "below_min"
def test_bad_date(): assert any(x["code"] == "type" for x in validate(C,{"id":"1","when":"2026-99-99"}))
def test_unknown(): assert any(x["code"] == "unknown" for x in validate(C,{"id":"1","when":"2026-01-01","x":2}))
def test_allow_unknown(): assert validate(C,{"id":"1","when":"2026-01-01","x":2},False) == []
def test_profile():
 p=profile(C,[{"id":"1","when":"2026-01-01"}, {"id":"0","when":"bad"}]);assert (p["rows"],p["valid_rows"]) == (2,1)
