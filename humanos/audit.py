"""Opt-in local audit metadata; no prompts, tool names, arguments or results.
Use a database path in a trusted, user-private directory. Not tamper-proof.
"""
import sqlite3
from contextlib import closing
from pathlib import Path


class AuditLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        with closing(self._connect()) as db, db:
            db.execute("""CREATE TABLE IF NOT EXISTS agent_audit (
                session TEXT NOT NULL, sequence INTEGER NOT NULL,
                outcome TEXT NOT NULL CHECK(outcome IN ('started','succeeded','denied','failed')),
                PRIMARY KEY(session, sequence))""")

    def _connect(self):
        return sqlite3.connect(self.path)

    def start(self, session: str, sequence: int):
        with closing(self._connect()) as db, db:
            db.execute("INSERT INTO agent_audit VALUES (?, ?, 'started')", (session, sequence))

    def finish(self, session: str, sequence: int, outcome: str):
        if outcome not in ('succeeded', 'denied', 'failed'):
            raise ValueError('Invalid final outcome')
        with closing(self._connect()) as db, db:
            changed = db.execute("UPDATE agent_audit SET outcome=? WHERE session=? AND sequence=? AND outcome='started'",
                                 (outcome, session, sequence)).rowcount
            if changed != 1:
                raise RuntimeError('Missing or finalized audit event')

    def events(self, session: str):
        with closing(self._connect()) as db:
            return db.execute('SELECT sequence, outcome FROM agent_audit WHERE session=? ORDER BY sequence', (session,)).fetchall()
