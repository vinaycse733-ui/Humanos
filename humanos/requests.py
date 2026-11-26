"""Strict JSON boundary for untrusted model tool requests."""
import json


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError('Non-finite JSON constant')


def parse_request(raw: str) -> tuple[str, dict]:
    if type(raw) is not str or len(raw) > 16384:
        raise ValueError('Invalid request size or type')
    try:
        obj = json.loads(raw, object_pairs_hook=_unique, parse_constant=_reject_constant)
    except (RecursionError, OverflowError) as exc:
        raise ValueError('Invalid JSON nesting or number') from exc
    if type(obj) is not dict or set(obj) != {'tool', 'arguments'}:
        raise ValueError('Expected tool and arguments only')
    name, args = obj['tool'], obj['arguments']
    if type(name) is not str or not name or len(name) > 128 or type(args) is not dict:
        raise ValueError('Invalid tool request')
    return name, args


def execute_request(session, raw: str):
    """Dispatch once through an existing session; never grant permissions."""
    name, args = parse_request(raw)
    return session.execute(name, args)
