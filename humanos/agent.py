"""Bounded execution of explicit tool requests; no shell or model-driven grants."""
from dataclasses import dataclass
from threading import Lock
from uuid import uuid4
from .permissions import ToolRunner
from .audit import AuditLog

@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    outcome: str

class AgentSession:
    def __init__(self, runner: ToolRunner, limit: int = 20, *, journal: AuditLog | None = None):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('Invalid execution limit')
        self._runner = runner
        self._limit = limit
        self._events = []
        self._lock = Lock()
        self._journal = journal
        self._session_id = uuid4().hex
        self._audit_failed = False

    @property
    def session_id(self):
        return self._session_id

    @property
    def audit(self):
        with self._lock:
            return tuple(self._events)

    def execute(self, name: str, arguments: dict):
        with self._lock:
            if self._audit_failed:
                raise RuntimeError('Audit unavailable; session stopped')
            if len(self._events) >= self._limit:
                raise RuntimeError('Session execution budget exhausted')
            sequence = len(self._events) + 1
            if self._journal is not None:
                self._journal.start(self._session_id, sequence)
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
                if self._journal is not None:
                    try:
                        self._journal.finish(self._session_id, sequence, outcome)
                    except Exception as exc:
                        self._audit_failed = True
                        raise RuntimeError('Audit completion failed; action may have occurred; do not retry blindly') from exc
