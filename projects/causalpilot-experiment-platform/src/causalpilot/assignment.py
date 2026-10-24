"""Deterministic and auditable 2-arm assignment."""
import hashlib
import hmac
from .models import Experiment, check_id


def arm(config: Experiment, subject_id: str) -> str:
    check_id(subject_id, "subject_id")
    payload = f"{config.experiment_id}\0{subject_id}".encode("utf-8")
    digest = hmac.new(config.salt.encode("utf-8"), payload, hashlib.sha256).digest()
    bucket = int.from_bytes(digest[:8], "big") / 2**64
    return "B" if bucket < config.treatment_fraction else "A"
