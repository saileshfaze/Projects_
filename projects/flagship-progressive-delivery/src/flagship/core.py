"""Deterministic feature flag evaluation and progressive rollout rules."""
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any
import json

@dataclass(frozen=True)
class Rule:
    attribute: str
    operator: str
    value: Any
    variation: str

@dataclass
class Flag:
    key: str
    variations: dict[str, Any]
    default: str
    enabled: bool = True
    rules: list[Rule] = field(default_factory=list)
    rollout: dict[str, int] = field(default_factory=dict)
    salt: str = "v1"

    def validate(self):
        if not self.key or self.default not in self.variations:
            raise ValueError("Invalid key/default")
        if any(x not in self.variations for x in self.rollout):
            raise ValueError("Unknown rollout variation")
        if any(not isinstance(x, int) or x < 0 for x in self.rollout.values()):
            raise ValueError("Rollout weights must be nonnegative integers")
        if sum(self.rollout.values()) > 10000:
            raise ValueError("Rollout exceeds 100 percent")
        for rule in self.rules:
            if rule.variation not in self.variations or rule.operator not in ('eq', 'in', 'gte', 'lte'):
                raise ValueError("Invalid rule")

@dataclass(frozen=True)
class Decision:
    flag: str
    variation: str
    value: Any
    reason: str
    bucket: int | None = None

def bucket(flag: Flag, subject: str) -> int:
    if not subject:
        raise ValueError("Subject must be nonempty")
    digest = sha256(f'{flag.salt}:{flag.key}:{subject}'.encode()).digest()
    return int.from_bytes(digest[:8], 'big') % 10000

def matches(rule: Rule, context: dict) -> bool:
    if rule.attribute not in context:
        return False
    actual = context[rule.attribute]
    try:
        return {'eq': lambda: actual == rule.value,
                'in': lambda: actual in rule.value,
                'gte': lambda: actual >= rule.value,
                'lte': lambda: actual <= rule.value}[rule.operator]()
    except (TypeError, KeyError):
        return False

def evaluate(flag: Flag, subject: str, context: dict | None = None) -> Decision:
    flag.validate()
    if not flag.enabled:
        return Decision(flag.key, flag.default, flag.variations[flag.default], 'disabled')
    for rule in flag.rules:
        if matches(rule, context or {}):
            return Decision(flag.key, rule.variation, flag.variations[rule.variation], 'rule')
    b = bucket(flag, subject)
    cumulative = 0
    for variation, weight in sorted(flag.rollout.items()):
        cumulative += weight
        if b < cumulative:
            return Decision(flag.key, variation, flag.variations[variation], 'rollout', b)
    return Decision(flag.key, flag.default, flag.variations[flag.default], 'default', b)

def from_dict(data: dict) -> Flag:
    d = data.copy()
    d['rules'] = [Rule(**x) for x in d.get('rules', [])]
    f = Flag(**d)
    f.validate()
    return f

def load_flags(path: str) -> dict[str, Flag]:
    data = json.loads(open(path, encoding='utf-8').read())
    flags = [from_dict(item) for item in data['flags']]
    if len({f.key for f in flags}) != len(flags):
        raise ValueError('Duplicate keys')
    return {f.key: f for f in flags}
