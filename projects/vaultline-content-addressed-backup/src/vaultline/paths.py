"""Safe relative path handling, including traversal and symlink rejection."""
from pathlib import Path, PurePosixPath
from .errors import VaultlineError

def safe_relative(raw: str) -> PurePosixPath:
    if not isinstance(raw, str) or not raw or "\\" in raw or "\x00" in raw:
        raise VaultlineError("invalid path")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(p in ("..", ".", "") for p in raw.split("/")) or ":" in path.parts[0]:
        raise VaultlineError("unsafe relative path")
    return path

def safe_target(root: Path, relative: str) -> Path:
    path = safe_relative(relative)
    target = root.joinpath(*path.parts)
    for ancestor in (root, *list(target.parents)[:-1]):
        if ancestor.is_symlink():
            raise VaultlineError("symlink in restore path")
    if target.is_symlink():
        raise VaultlineError("symlink restore target")
    return target
