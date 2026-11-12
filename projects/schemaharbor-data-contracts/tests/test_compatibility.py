from schemaharbor.contracts import Contract
from schemaharbor.compatibility import compare, recommendation

def c(fields): return Contract.from_dict({"name":"orders","version":"1","fields":fields})
def f(kind="integer", **kw): return {"name":"amount","kind":kind,**kw}
def test_same(): assert recommendation(compare(c([f()]),c([f()]))) == "patch"
def test_widen(): assert recommendation(compare(c([f()]),c([f("number")]))) == "minor"
def test_narrow(): assert recommendation(compare(c([f("number")]),c([f()]))) == "major"
def test_required_add(): assert recommendation(compare(c([]),c([f()]))) == "major"
def test_optional_add(): assert recommendation(compare(c([]),c([f(required=False)]))) == "minor"
def test_remove(): assert recommendation(compare(c([f()]),c([]))) == "major"
def test_tighten(): assert recommendation(compare(c([f(minimum=0)]),c([f(minimum=1)]))) == "major"
def test_relax(): assert recommendation(compare(c([f(minimum=0)]),c([f(minimum=-1)]))) == "minor"
def test_nullable(): assert recommendation(compare(c([f(nullable=True)]),c([f(nullable=False)]))) == "major"
