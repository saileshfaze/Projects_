"""Explicit JSON export for simulation reproducibility (not Raft disk durability)."""
from __future__ import annotations
import json
from pathlib import Path
from .raft import Cluster
from .metrics import evaluate


def export_run(cluster: Cluster, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": 1, "seed": cluster.seed, "summary": cluster.summary(),
            "metrics": evaluate(cluster), "timeline": cluster.timeline,
            "audit": cluster.audit.records,
            "logs": {key: [entry.to_dict() for entry in node.log] for key, node in cluster.nodes.items()}}
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def verify_export(path: str | Path) -> bool:
    from .audit import AuditChain
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        return False
    chain = AuditChain()
    chain.records = data["audit"]
    return chain.verify() and data["summary"]["audit_valid"] is True
