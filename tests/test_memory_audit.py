import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from humanos.agent import AgentSession
from humanos.audit import AuditLog
from humanos.memory import Memory
from humanos.memory_tools import memory_runner
from humanos.requests import execute_request


class MemoryAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.memory = Memory(Path(self.tmp.name) / 'memory.db')
        self.path = Path(self.tmp.name) / 'audit.db'
        self.log = AuditLog(self.path)

    def test_real_memory_and_durable_audit(self):
        session = AgentSession(memory_runner(self.memory, ['memory.write', 'memory.read']), journal=self.log)
        note = execute_request(session, json.dumps({'tool': 'memory.add', 'arguments': {'body': 'private-note'}}))
        self.assertEqual(execute_request(session, '{"tool":"memory.search","arguments":{"query":"private"}}'), [{'id': note, 'body': 'private-note'}])
        with self.assertRaises(PermissionError):
            session.execute('memory.delete', {'note_id': note})
        with self.assertRaises(ValueError):
            session.execute('memory.search', {'query': ''})
        self.assertEqual(AuditLog(self.path).events(session.session_id), [(1, 'succeeded'), (2, 'succeeded'), (3, 'denied'), (4, 'failed')])
        self.assertNotIn(b'private-note', self.path.read_bytes())
        self.assertEqual(len(self.memory.search()), 1)
        deletion = AgentSession(memory_runner(self.memory, ['memory.delete']), journal=self.log)
        self.assertTrue(deletion.execute('memory.delete', {'note_id': note}))
        self.assertEqual(self.memory.search(), [])

    def test_start_failure_prevents_side_effect(self):
        session = AgentSession(memory_runner(self.memory, ['memory.write']), journal=self.log)
        with patch.object(self.log, 'start', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                session.execute('memory.add', {'body': 'never written'})
        self.assertEqual(self.memory.search(), [])
        self.assertEqual(session.audit, ())

    def test_finish_failure_stops_future_actions(self):
        session = AgentSession(memory_runner(self.memory, ['memory.write']), journal=self.log)
        with patch.object(self.log, 'finish', side_effect=OSError('disk failure')):
            with self.assertRaisesRegex(RuntimeError, 'action may have occurred'):
                session.execute('memory.add', {'body': 'written'})
        with self.assertRaisesRegex(RuntimeError, 'session stopped'):
            session.execute('memory.add', {'body': 'not written'})
        self.assertEqual(len(self.memory.search()), 1)
        self.assertEqual(self.log.events(session.session_id), [(1, 'started')])
