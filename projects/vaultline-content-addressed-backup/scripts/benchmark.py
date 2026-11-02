"""Reproducible demonstration only; not a storage performance benchmark."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from vaultline.engine import Vault
from vaultline.synthetic import generate
with TemporaryDirectory() as temp:
    root=Path(temp); generate(root/'sample', files=40)
    vault=Vault(root/'vault'); vault.snapshot(root/'sample'); vault.snapshot(root/'sample')
    stats=vault.stats()
    print(json.dumps({**stats, 'logical_to_physical_ratio': round(stats['logical_bytes']/max(stats['stored_bytes'],1),3)}, indent=2))
