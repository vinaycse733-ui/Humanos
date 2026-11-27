"""Bounded execution of explicit tool requests; no shell or model-driven grants."""
from dataclasses import dataclass
from threading import Lock
from .permissions import ToolRunner

@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    outcome: str

class AgentSession:
    def __init__(self, runner: ToolRunner, limit: int = 20):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('Invalid execution limit')
        self._runner = runner
        self._limit = limit
        self._events = []
        self._lock = Lock()

    @property
    def audit(self):
        with self._lock:
            return tuple(self._events)

    def execute(self, name: str, arguments: dict):
        with self._lock:
            if len(self._events) >= self._limit:
                raise RuntimeError('Session execution budget exhausted')
            sequence = len(self._events) + 1
            self._events.append(AuditEvent(sequence, 'started'))
        outcome = 'failed'
        try:
            result = self._runner.execute(name, arguments)
            outcome = 'succeeded'
            return result
        except PermissionError:
            outcome = 'denied'
            raise
        finally:
            with self._lock:
                self._events[sequence - 1] = AuditEvent(sequence, outcome)
