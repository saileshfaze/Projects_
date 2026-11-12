"""Small strict JSON contract model, without network/schema registry dependencies."""
import json
from dataclasses import dataclass
from pathlib import Path

TYPES = {"string", "integer", "number", "boolean", "date"}

@dataclass(frozen=True)
class Field:
    name: str
    kind: str
    required: bool = True
    nullable: bool = False
    minimum: float | None = None
    maximum: float | None = None

    def __post_init__(self):
        if not self.name or not self.name.isidentifier():
            raise ValueError("invalid field name")
        if self.kind not in TYPES:
            raise ValueError("unsupported field type")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("invalid numeric bounds")
        if self.kind not in ("integer", "number") and (self.minimum is not None or self.maximum is not None):
            raise ValueError("bounds require numeric type")

@dataclass(frozen=True)
class Contract:
    name: str
    version: str
    fields: tuple[Field, ...]

    def __post_init__(self):
        if not self.name or not self.version:
            raise ValueError("name and version required")
        if len({f.name for f in self.fields}) != len(self.fields):
            raise ValueError("duplicate field")

    @classmethod
    def from_dict(cls, data):
        if set(data) != {"name", "version", "fields"} or not isinstance(data["fields"], list):
            raise ValueError("contract requires name, version and fields")
        allowed = {"name", "kind", "required", "nullable", "minimum", "maximum"}
        fields = []
        for entry in data["fields"]:
            if not isinstance(entry, dict) or not set(entry) <= allowed or not {"name", "kind"} <= set(entry):
                raise ValueError("invalid field definition")
            fields.append(Field(**entry))
        return cls(data["name"], data["version"], tuple(fields))

    @classmethod
    def load(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def to_dict(self):
        from dataclasses import asdict
        return {"name": self.name, "version": self.version, "fields": [asdict(f) for f in self.fields]}
