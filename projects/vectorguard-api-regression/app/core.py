"""Contract compatibility and offline lexical drift evaluation."""
import json
from difflib import SequenceMatcher

from .schema import changes, infer
from .drift import lexical_similarity


def fingerprint(payload):
    return infer([payload])


def evaluate_samples(baseline, candidate, lexical_limit=0.55):
    if not 0 <= lexical_limit <= 1:
        raise ValueError("lexical_limit must be between zero and one")
    old, new = infer(baseline), infer(candidate)
    findings = changes(old, new)

    def strings(samples):
        found = []
        def visit(value):
            if isinstance(value, str):
                found.append(value)
            elif isinstance(value, dict):
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)
        for sample in samples:
            visit(sample)
        return " ".join(found)

    similarity = lexical_similarity(strings(baseline), strings(candidate))
    breaking = any(f["severity"] == "breaking" for f in findings)
    drift = similarity < lexical_limit
    return {
        "breaking": breaking,
        "structure_changed": old != new,
        "changes": findings,
        "baseline_schema": old,
        "candidate_schema": new,
        "lexical_drift": {
            "backend": "token_bigram_cosine",
            "similarity": similarity,
            "threshold": lexical_limit,
            "drift_detected": drift,
        },
        "verdict": "fail" if breaking or drift else "pass",
    }


def compare(before, after):
    report = evaluate_samples([before], [after])
    report["text_similarity"] = round(
        SequenceMatcher(None, json.dumps(before, sort_keys=True), json.dumps(after, sort_keys=True)).ratio(),
        6,
    )
    return report
