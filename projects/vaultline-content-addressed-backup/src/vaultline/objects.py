"""Immutable SHA-256 object store with atomic writes and read verification."""
from pathlib import Path
import os
import tempfile
from .chunking import sha256
from .errors import IntegrityError, VaultlineError

class ObjectStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, digest: str) -> Path:
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise VaultlineError("invalid object digest")
        return self.root / digest[:2] / digest[2:]

    def put(self, data: bytes) -> str:
        digest = sha256(data)
        path = self.path(digest)
        if path.exists():
            self.get(digest)
            return digest
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".part-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        return digest

    def get(self, digest: str) -> bytes:
        path = self.path(digest)
        if path.is_symlink():
            raise IntegrityError("object is a symlink")
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise IntegrityError(f"missing object: {digest}") from exc
        if sha256(data) != digest:
            raise IntegrityError(f"corrupt object: {digest}")
        return data

    def remove(self, digest: str) -> None:
        self.path(digest).unlink(missing_ok=True)

    def all_digests(self):
        for directory in sorted(self.root.iterdir()):
            if directory.is_dir() and len(directory.name) == 2:
                for file in sorted(directory.iterdir()):
                    digest = directory.name + file.name
                    if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
                        yield digest
