"""Create a small, fictional operations knowledge base and golden relevance judgments."""
from __future__ import annotations
import json
from pathlib import Path

DOCS = [
    ("cache-ttl", "Redis cache expiration", "Redis cache entries expire after fifteen minutes. Invalidation is triggered immediately after a successful write transaction.", "platform"),
    ("cache-eviction", "Cache memory pressure", "The cache uses an allkeys-lru eviction policy when memory reaches the configured limit. Cache hit rate is measured every minute.", "platform"),
    ("incident-sev1", "Critical incident response", "Severity one incidents require acknowledgement within five minutes. The incident commander posts updates every fifteen minutes.", "incident"),
    ("incident-sev2", "High severity incidents", "Severity two incidents require acknowledgement within thirty minutes. The primary on-call engineer coordinates the response.", "incident"),
    ("backup-policy", "Database backup retention", "Database snapshots are taken every six hours. Daily backups are retained for thirty days and monthly backups for one year.", "storage"),
    ("restore-policy", "Database restore procedure", "Restore rehearsals run every quarter in an isolated staging environment. The recovery point objective is six hours.", "storage"),
    ("deploy-rollout", "Progressive deployment", "Deployments begin with five percent of traffic. The rollout pauses automatically when the five-minute error rate exceeds two percent.", "delivery"),
    ("deploy-rollback", "Deployment rollback", "Rollback starts when latency exceeds the agreed service objective for ten consecutive minutes. The last stable release is restored.", "delivery"),
    ("access-policy", "Service access reviews", "Service accounts are reviewed every ninety days. Access grants must have an owner and an expiration date.", "security"),
    ("key-rotation", "API key rotation", "Production API keys rotate every sixty days. Revoked keys cannot authenticate after the next cache refresh.", "security"),
    ("alert-routing", "Alert routing", "Alerts for payment services are sent to the payments on-call rotation. Non-urgent alerts are grouped into hourly summaries.", "observability"),
    ("slo-budget", "Service level objectives", "The checkout service targets 99.9 percent availability over thirty days. Error budget burn is calculated using five-minute and one-hour windows.", "observability"),
]
QUESTIONS = [
    ("q01", "When do redis cache entries expire?", "direct", ["cache-ttl"]),
    ("q02", "What happens under cache memory pressure?", "direct", ["cache-eviction"]),
    ("q03", "How quickly must severity one incidents be acknowledged?", "direct", ["incident-sev1"]),
    ("q04", "How long are monthly database backups retained?", "direct", ["backup-policy"]),
    ("q05", "What is the recovery point objective?", "direct", ["restore-policy"]),
    ("q06", "When does a deployment rollout pause?", "direct", ["deploy-rollout"]),
    ("q07", "How often are API keys rotated?", "direct", ["key-rotation"]),
    ("q08", "What is the checkout service availability target?", "direct", ["slo-budget"]),
    ("q09", "How often are service accounts reviewed?", "direct", ["access-policy"]),
    ("q10", "Where do payment service alerts go?", "direct", ["alert-routing"]),
    ("q11", "redis cach expiratn", "typo", ["cache-ttl"]),
    ("q12", "sev 2 acknowledge", "abbreviated", ["incident-sev2"]),
    ("q13", "What is the rollback latency condition?", "direct", ["deploy-rollback"]),
    ("q14", "What is the company's vacation policy?", "unanswerable", []),
]

def generate(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    docs = [{"id": id_, "title": title, "body": body,
             "source": "fictional-ops-handbook", "category": category}
            for id_, title, body, category in DOCS]
    questions = [{"id": id_, "question": question, "slice": slice_}
                 for id_, question, slice_, _ in QUESTIONS]
    qrels = [{"id": id_, "relevant": ids} for id_, _, _, ids in QUESTIONS]
    for name, rows in (("documents", docs), ("questions", questions), ("qrels", qrels)):
        (destination / f"{name}.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")

if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "data")
