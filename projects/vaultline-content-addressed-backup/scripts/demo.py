import json
from pathlib import Path
from tempfile import TemporaryDirectory
from vaultline.engine import Vault
from vaultline.synthetic import generate
from vaultline.report import svg_report

with TemporaryDirectory() as base:
    root=Path(base)
    generate(root/'source')
    vault=Vault(root/'vault')
    first=vault.snapshot(root/'source', 'baseline')
    (root/'source'/'batch-00'/'record-000.csv').write_text('changed sample')
    second=vault.snapshot(root/'source', 'changed')
    verified=vault.verify(second['id'])
    restored=vault.restore(first['id'], root/'restore')
    assert (root/'restore'/'batch-00'/'record-000.csv').read_text() != 'changed sample'
    (root/'inventory.svg').write_text(svg_report(vault))
    print(json.dumps(dict(first=first, second=second, verified=verified, restored_files=restored['files'], stats=vault.stats(), audit_events=vault.audit.verify()), indent=2))
