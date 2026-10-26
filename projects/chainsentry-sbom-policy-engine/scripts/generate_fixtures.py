"""Rebuild synthetic CycloneDX/SPDX SBOMs and a fictional advisory feed."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "examples"


def write(name: str, payload: dict) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate() -> None:
    # All package names and advisories below are fictional, not real security intelligence.
    items = [
        ("app", "shopfront", "1.0.0", "pkg:pypi/shopfront@1.0.0", "MIT"),
        ("web", "displaykit", "2.1.0", "pkg:pypi/displaykit@2.1.0", "Apache-2.0"),
        ("core", "querybolt", "1.4.2", "pkg:pypi/querybolt@1.4.2", "MIT"),
        ("crypto", "cipherleaf", "0.8.1", "pkg:pypi/cipherleaf@0.8.1", "BSD-3-Clause"),
        ("log", "tracelog", "3.0.0", "pkg:pypi/tracelog@3.0.0", "GPL-3.0-only"),
        ("unused", "ghostcache", "0.1.0", "pkg:pypi/ghostcache@0.1.0", "MIT"),
    ]
    cyclonedx = {"bomFormat": "CycloneDX", "specVersion": "1.5", "version": 1,
                 "metadata": {"component": {"bom-ref": "app", "name": "shopfront"}},
                 "components": [{"bom-ref": ref, "name": name, "version": version, "purl": purl,
                                 "licenses": [{"license": {"id": license_id}}]}
                                for ref, name, version, purl, license_id in items],
                 "dependencies": [{"ref": "app", "dependsOn": ["web", "core"]},
                                  {"ref": "web", "dependsOn": ["crypto", "log"]},
                                  {"ref": "core", "dependsOn": ["crypto"]}]}
    spdx = {"spdxVersion": "SPDX-2.3", "SPDXID": "SPDXRef-DOCUMENT", "name": "shopfront",
            "documentDescribes": ["SPDXRef-app"],
            "packages": [{"SPDXID": f"SPDXRef-{ref}", "name": name, "versionInfo": version,
                          "licenseConcluded": license_id,
                          "externalRefs": [{"referenceType": "purl", "referenceLocator": purl}]}
                         for ref, name, version, purl, license_id in items],
            "relationships": [{"spdxElementId": f"SPDXRef-{src}", "relatedSpdxElement": f"SPDXRef-{dst}",
                               "relationshipType": "DEPENDS_ON"}
                              for src, dst in [("app", "web"), ("app", "core"), ("web", "crypto"),
                                               ("web", "log"), ("core", "crypto")]]}
    feed = {"feed_type": "synthetic-demo", "advisories": [
        {"id": "DEMO-2026-0001", "purl_name": "pypi/cipherleaf", "introduced": "0", "fixed": "0.9.0",
         "severity": "critical", "summary": "Fictional cryptographic validation flaw"},
        {"id": "DEMO-2026-0002", "purl_name": "pypi/ghostcache", "introduced": "0", "fixed": "0.2.0",
         "severity": "high", "summary": "Fictional cache isolation flaw"},
        {"id": "DEMO-2026-0003", "purl_name": "pypi/displaykit", "introduced": "2.0.0", "fixed": "2.1.0",
         "severity": "medium", "summary": "Fictional issue fixed in the sample version"}]}
    policy = {"fail_at": "high", "deny_licenses": ["GPL-3.0-only"], "require_license": True,
              "require_purl": True, "fail_unreachable": False, "exemptions": []}
    exempt_policy = {**policy, "exemptions": [{"advisory": "DEMO-2026-0001",
                    "purl": "pkg:pypi/cipherleaf@0.8.1", "expires": "2027-01-01",
                    "justification": "Demo-only exception to exercise expiry handling"}]}
    for name, data in [("cyclonedx.json", cyclonedx), ("spdx.json", spdx),
                       ("advisories.json", feed), ("policy.json", policy), ("policy-exemption.json", exempt_policy)]:
        write(name, data)


if __name__ == "__main__":
    generate()
