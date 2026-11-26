import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch
from humanos.memory_cli import main


class MemoryCliTests(unittest.TestCase):
    def test_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'notes.db'
            def run(*args, note=''):
                output = io.StringIO()
                with patch('sys.stdin', io.StringIO(note)), redirect_stdout(output):
                    self.assertEqual(main(['--db', str(db), *args]), 0)
                return json.loads(output.getvalue())
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(['--db', str(db), 'export']), 1)
            self.assertFalse(db.exists())
            ident = run('add', note='private')['id']
            self.assertEqual(run('search', 'PRIVATE'), [{'id': ident, 'body': 'private'}])
            self.assertEqual(run('export'), run('search'))
            self.assertEqual(run('delete', str(ident)), {'deleted': True})
            self.assertEqual(run('export'), [])
