"""Deterministic deny-overrides attribute-based authorization policy evaluator."""
from __future__ import annotations
from dataclasses import dataclass
from fnmatch import fnmatchcase
import json
from typing import Any

ALLOWED_OPS = {"eq", "ne", "in", "not_in", "gte", "lte", "contains", "exists"}

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    matched: tuple[str, ...]
    policy_version: str
    def as_dict(self):
        return {"allowed": self.allowed, "reason": self.reason, "matched": list(self.matched), "policy_version": self.policy_version}

class PolicyError(ValueError):
    pass

def _resolve(context: dict[str, Any], path: str):
    cur: Any = context
    for key in path.split('.'):
        if not isinstance(cur, dict) or key not in cur:
            return False, None
        cur = cur[key]
    return True, cur

def _predicate(predicate: dict[str, Any], context: dict[str, Any]) -> bool:
    op = predicate['op']
    found, actual = _resolve(context, predicate['path'])
    if op == 'exists':
        return found == predicate['value']
    if not found:
        return False
    expected = predicate['value']
    try:
        if op == 'eq': return actual == expected
        if op == 'ne': return actual != expected
        if op == 'in': return actual in expected
        if op == 'not_in': return actual not in expected
        if op == 'gte': return type(actual) in (int, float) and type(expected) in (int, float) and actual >= expected
        if op == 'lte': return type(actual) in (int, float) and type(expected) in (int, float) and actual <= expected
        if op == 'contains': return isinstance(actual, (list, str)) and expected in actual
    except (TypeError, ValueError):
        return False
    return False

def validate_policy(policy: dict[str, Any]) -> None:
    if not isinstance(policy, dict) or not isinstance(policy.get('version'), str) or not policy['version']:
        raise PolicyError('policy.version must be a nonempty string')
    rules = policy.get('rules')
    if not isinstance(rules, list): raise PolicyError('rules must be a list')
    seen = set()
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get('id'), str) or not rule['id'] or rule['id'] in seen:
            raise PolicyError('rule ids must be unique nonempty strings')
        seen.add(rule['id'])
        if rule.get('effect') not in ('allow', 'deny'): raise PolicyError('invalid effect')
        for key in ('actions', 'resources'):
            if not isinstance(rule.get(key), list) or not rule[key] or any(not isinstance(x, str) or not x for x in rule[key]):
                raise PolicyError(f'{key} must be nonempty string list')
        predicates = rule.get('when', [])
        if not isinstance(predicates, list): raise PolicyError('when must be a list')
        for pred in predicates:
            if not isinstance(pred, dict) or pred.get('op') not in ALLOWED_OPS or not isinstance(pred.get('path'), str) or not pred['path'] or 'value' not in pred:
                raise PolicyError('invalid predicate')
            if pred['op'] == 'exists' and type(pred['value']) is not bool: raise PolicyError('exists requires bool')
            if pred['op'] in ('in', 'not_in') and not isinstance(pred['value'], list): raise PolicyError('membership requires list')

def evaluate(policy: dict[str, Any], request: dict[str, Any]) -> Decision:
    validate_policy(policy)
    if not isinstance(request, dict) or any(k not in request for k in ('action', 'resource', 'subject')):
        raise PolicyError('request requires action, resource and subject')
    if not isinstance(request['action'], str) or not isinstance(request['resource'], str) or not isinstance(request['subject'], dict):
        raise PolicyError('invalid request fields')
    matches = []
    effects = []
    context = {'subject': request['subject'], 'environment': request.get('environment', {}), 'resource_attributes': request.get('resource_attributes', {})}
    for rule in policy['rules']:
        if (any(fnmatchcase(request['action'], x) for x in rule['actions'])
            and any(fnmatchcase(request['resource'], x) for x in rule['resources'])
            and all(_predicate(p, context) for p in rule.get('when', []))):
            matches.append(rule['id'])
            effects.append(rule['effect'])
    if 'deny' in effects: return Decision(False, 'explicit_deny', tuple(matches), policy['version'])
    if 'allow' in effects: return Decision(True, 'explicit_allow', tuple(matches), policy['version'])
    return Decision(False, 'default_deny', (), policy['version'])

def evaluate_batch(policy: dict[str, Any], requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_policy(policy)
    return [evaluate(policy, req).as_dict() for req in requests]

def canonical_report(policy: dict[str, Any], requests: list[dict[str, Any]]) -> str:
    return json.dumps({'version': policy['version'], 'decisions': evaluate_batch(policy, requests)}, sort_keys=True, indent=2) + '\n'
