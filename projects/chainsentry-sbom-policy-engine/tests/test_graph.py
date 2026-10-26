from chainsentry.graph import shortest_paths, strongly_connected_components
from chainsentry.models import BillOfMaterials, Component
from chainsentry.parser import parse_sbom


def test_reachability(fixture_data):
    paths = shortest_paths(parse_sbom(fixture_data("cyclonedx.json")))
    assert paths["crypto"] == ("app", "core", "crypto")
    assert "unused" not in paths


def test_scc_cycle():
    comps = {x: Component(x, x, "1", "") for x in "abc"}
    bom = BillOfMaterials("test", comps, {"a": ("b",), "b": ("a",), "c": ()}, ("a",))
    assert strongly_connected_components(bom) == [("a", "b"), ("c",)]
    assert len(shortest_paths(bom)) == 2


def test_singletons(fixture_data):
    bom = parse_sbom(fixture_data("cyclonedx.json"))
    assert len(strongly_connected_components(bom)) == 6
