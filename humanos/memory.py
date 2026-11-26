"""Explicit, local memory storage. No automatic prompt retention."""
import sqlite3
from contextlib import closing
from pathlib import Path

class Memory:
    def __init__(self, path: Path):
        self.path = Path(path)
        with closing(self._connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL)")

    def _connect(self):
        return sqlite3.connect(self.path)

    def add(self, body: str) -> int:
        if not body.strip() or len(body) > 100000:
            raise ValueError("Note must contain 1–100000 characters")
        with closing(self._connect()) as db, db:
            return db.execute("INSERT INTO notes(body) VALUES (?)", (body,)).lastrowid

    def search(self, query: str = "") -> list[dict]:
        with closing(self._connect()) as db:
            return [{"id": i, "body": b} for i, b in db.execute(
                "SELECT id, body FROM notes WHERE instr(lower(body), lower(?)) > 0 OR ? = '' ORDER BY id", (query, query))]

    def delete(self, note_id: int) -> bool:
        with closing(self._connect()) as db, db:
            db.execute("PRAGMA secure_delete=ON")
            return db.execute("DELETE FROM notes WHERE id=?", (note_id,)).rowcount == 1
