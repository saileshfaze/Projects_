"""Compare tracked sample CSVs with a fresh deterministic regeneration."""
import tempfile
from pathlib import Path
from generate_data import run

def verify():
    expected=Path('data/synthetic')
    with tempfile.TemporaryDirectory() as tmp:
        run(tmp)
        for name in ('baseline.csv','production.csv','labels.csv'):
            source=expected/name;regenerated=Path(tmp)/name
            if not source.is_file() or source.read_bytes()!=regenerated.read_bytes():
                raise AssertionError(f'synthetic asset mismatch: {name}')
    return True
if __name__=='__main__':
    verify();print('3 synthetic CSV assets match fixed-seed generation')
