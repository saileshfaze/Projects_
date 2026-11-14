"""Small-record FASTA parser with strict validation."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from .sequence import normalize

@dataclass(frozen=True)
class Record:
    identifier: str
    sequence: str


def parse_fasta(lines: Iterable[str], max_length: int = 1_000_000) -> list[Record]:
    if max_length < 1:
        raise ValueError("max_length must be positive")
    result: list[Record] = []
    seen: set[str] = set()
    identifier: str | None = None
    chunks: list[str] = []
    length = 0

    def flush() -> None:
        if identifier is not None:
            result.append(Record(identifier, normalize("".join(chunks))))

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            flush()
            identifier = line[1:].split(maxsplit=1)[0] if line[1:].strip() else ""
            if not identifier or identifier in seen:
                raise ValueError("empty or duplicate FASTA identifier")
            seen.add(identifier)
            chunks = []
            length = 0
        else:
            if identifier is None:
                raise ValueError("sequence before FASTA header")
            length += len(line)
            if length > max_length:
                raise ValueError("FASTA record exceeds max_length")
            chunks.append(line)
    flush()
    if not result:
        raise ValueError("FASTA contains no records")
    return result


def read_fasta(path: str | Path, max_length: int = 1_000_000) -> list[Record]:
    with Path(path).open(encoding="utf-8") as handle:
        return parse_fasta(handle, max_length)
