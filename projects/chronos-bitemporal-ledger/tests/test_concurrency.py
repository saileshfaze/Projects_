from concurrent.futures import ThreadPoolExecutor

from chronos_ledger.audit import verify
from chronos_ledger.models import Correction


def test_parallel_writes_preserve_tenant_chain(ledger):
    def write(i):
        return ledger.correct(
            "t", f"entity-{i}", Correction(
                valid_from="2026-01-01", valid_to="2027-01-01",
                payload={"index": i}, actor="worker", idempotency_key=f"task-{i}",
            ),
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(write, range(12)))
    assert len({r.operation_id for r in receipts}) == 12
    assert verify(ledger.path, "t").valid
