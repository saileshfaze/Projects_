import copy
import pytest
from chainsentry.parser import parse_sbom, SBOMError


def test_cyclonedx_normalizes(fixture_data):
    bom = parse_sbom(fixture_data("cyclonedx.json"))
    assert len(bom.components) == 6
    assert bom.roots == ("app",)
    assert bom.dependencies["app"] == ("core", "web")


def test_spdx_normalizes(fixture_data):
    bom = parse_sbom(fixture_data("spdx.json"))
    assert bom.format == "spdx"
    assert len(bom.components) == 6
    assert bom.components["SPDXRef-crypto"].licenses == ("BSD-3-Clause",)


def test_unknown_format():
    with pytest.raises(SBOMError):
        parse_sbom({"other": "document"})


def test_missing_components(fixture_data):
    data = fixture_data("cyclonedx.json")
    data["components"] = []
    with pytest.raises(SBOMError):
        parse_sbom(data)


def test_duplicate_ref(fixture_data):
    data = fixture_data("cyclonedx.json")
    data["components"].append(copy.deepcopy(data["components"][0]))
    with pytest.raises(SBOMError, match="duplicate"):
        parse_sbom(data)


def test_dangling_dependency(fixture_data):
    data = fixture_data("cyclonedx.json")
    data["dependencies"][0]["dependsOn"].append("not-there")
    with pytest.raises(SBOMError, match="unknown dependency"):
        parse_sbom(data)


def test_inferred_roots(fixture_data):
    data = fixture_data("cyclonedx.json")
    data.pop("metadata")
    assert parse_sbom(data).roots == ("app", "unused")


def test_invalid_spdx_relationship(fixture_data):
    data = fixture_data("spdx.json")
    data["relationships"].append({"relationshipType": "DEPENDS_ON", "spdxElementId": "SPDXRef-app", "relatedSpdxElement": "MISSING"})
    with pytest.raises(SBOMError):
        parse_sbom(data)


def test_spdx_reverse_dependency(fixture_data):
    data = fixture_data("spdx.json")
    data["relationships"] = [{"relationshipType": "DEPENDENCY_OF", "spdxElementId": "SPDXRef-crypto", "relatedSpdxElement": "SPDXRef-app"}]
    bom = parse_sbom(data)
    assert "SPDXRef-crypto" in bom.dependencies["SPDXRef-app"]
