"""Snapshot, verify, restore and prune operations with deduplicated objects."""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from .objects import ObjectStore
from .chunking import chunks, sha256
from .manifest import seal, verify as verify_manifest, canonical
from .paths import safe_relative, safe_target
from .audit import AuditLog
from .errors import VaultlineError, IntegrityError

class Vault:
    def __init__(self, root: str | Path, minimum=2048, average=8192, maximum=32768):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifests = self.root / "manifests"
        self.manifests.mkdir(exist_ok=True)
        self.store = ObjectStore(self.root / "objects")
        self.audit = AuditLog(self.root / "audit.sqlite3")
        self.config = (minimum, average, maximum)

    def snapshot(self, source: str | Path, label: str = "") -> dict:
        source = Path(source).resolve()
        if not source.is_dir() or source == self.root or self.root.is_relative_to(source) or source.is_relative_to(self.root):
            raise VaultlineError("source must be a separate directory outside the vault")
        if not isinstance(label, str) or len(label) > 100:
            raise VaultlineError("invalid label")
        files = []
        for base, dirs, names in os.walk(source, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
            for name in sorted(names):
                path = Path(base) / name
                if path.is_symlink() or not path.is_file():
                    continue
                rel = path.relative_to(source).as_posix()
                safe_relative(rel)
                data = path.read_bytes()
                digests = [self.store.put(part) for part in chunks(data, *self.config)]
                files.append(dict(path=rel, size=len(data), digest=sha256(data), chunks=digests))
        files.sort(key=lambda item: item["path"])
        payload = dict(version=1, created=datetime.now(timezone.utc).isoformat(), label=label, files=files, chunking=list(self.config))
        manifest = seal(payload)
        identifier = manifest["digest"]
        path = self.manifests / f"{identifier}.json"
        if not path.exists():
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(canonical(manifest) + b"\n")
            os.replace(tmp, path)
        self.audit.append("snapshot", {"id": identifier, "files": len(files)})
        return dict(id=identifier, files=len(files), bytes=sum(f["size"] for f in files), chunks=sum(len(f["chunks"]) for f in files))

    def load(self, identifier: str) -> dict:
        self.store.path(identifier)  # validates digest syntax
        try:
            manifest = json.loads((self.manifests / f"{identifier}.json").read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise IntegrityError("manifest missing or malformed") from exc
        verify_manifest(manifest)
        if manifest["digest"] != identifier or manifest.get("version") != 1:
            raise IntegrityError("manifest identifier or version mismatch")
        seen = set()
        for file in manifest["files"]:
            safe_relative(file["path"])
            if file["path"] in seen:
                raise IntegrityError("duplicate path")
            seen.add(file["path"])
        return manifest

    def list_snapshots(self) -> list[dict]:
        output = []
        for path in sorted(self.manifests.glob("*.json")):
            item = self.load(path.stem)
            output.append(dict(id=item["digest"], created=item["created"], label=item["label"], files=len(item["files"])))
        return sorted(output, key=lambda x: (x["created"], x["id"]))

    def verify(self, identifier: str) -> dict:
        manifest = self.load(identifier)
        total = 0
        for item in manifest["files"]:
            content = b"".join(self.store.get(digest) for digest in item["chunks"])
            if sha256(content) != item["digest"] or len(content) != item["size"]:
                raise IntegrityError(f"file checksum mismatch: {item['path']}")
            total += len(content)
        self.audit.append("verify", {"id": identifier, "bytes": total})
        return dict(id=identifier, files=len(manifest["files"]), bytes=total, ok=True)

    def restore(self, identifier: str, target: str | Path, overwrite=False) -> dict:
        manifest = self.load(identifier)
        target = Path(target).absolute()
        if target == self.root or target.is_relative_to(self.root) or self.root.is_relative_to(target):
            raise VaultlineError("restore target must not overlap vault")
        # Verify all content before creating any output files.
        self.verify(identifier)
        planned = [(safe_target(target, item["path"]), item) for item in manifest["files"]]
        if not overwrite and any(path.exists() for path, _ in planned):
            raise VaultlineError("restore target contains existing files")
        for path, item in planned:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Check again after directory creation, preventing accidental symlink traversal.
            safe_target(target, item["path"])
            temp = path.with_name(path.name + ".vaultline-tmp")
            try:
                with temp.open("wb") as stream:
                    for digest in item["chunks"]:
                        stream.write(self.store.get(digest))
                os.replace(temp, path)
            finally:
                temp.unlink(missing_ok=True)
        self.audit.append("restore", {"id": identifier, "files": len(planned)})
        return dict(id=identifier, files=len(planned), target=str(target))

    def prune(self, keep: int = 3, dry_run=True) -> dict:
        if not isinstance(keep, int) or keep < 0:
            raise VaultlineError("keep must be nonnegative")
        snapshots = self.list_snapshots()
        discarded = snapshots[:-keep] if keep else snapshots[:]
        remaining = snapshots[-keep:] if keep else []
        referenced = {digest for snap in remaining for item in self.load(snap["id"])["files"] for digest in item["chunks"]}
        obsolete = sorted(set(self.store.all_digests()) - referenced)
        if not dry_run:
            for item in discarded:
                (self.manifests / (item["id"] + ".json")).unlink()
            for digest in obsolete:
                self.store.remove(digest)
            self.audit.append("prune", {"removed_snapshots": len(discarded), "removed_objects": len(obsolete)})
        return dict(dry_run=dry_run, removed_snapshots=len(discarded), removed_objects=len(obsolete), retained_snapshots=len(remaining))

    def stats(self) -> dict:
        snaps = self.list_snapshots()
        unique = list(self.store.all_digests())
        return dict(snapshots=len(snaps), objects=len(unique), stored_bytes=sum(self.store.path(d).stat().st_size for d in unique), logical_bytes=sum(item["size"] for snap in snaps for item in self.load(snap["id"])["files"]))
