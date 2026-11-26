import unittest
from humanos.agent import AgentSession
from humanos.permissions import Tool, ToolRunner

class AgentTests(unittest.TestCase):
    def test_grants_and_budget(self):
        calls = []
        tools = {'note': Tool('write', lambda body: calls.append(body))}
        denied = AgentSession(ToolRunner(tools), 1)
        with self.assertRaises(PermissionError):
            denied.execute('note', {'body': 'secret'})
        self.assertEqual(calls, [])
        self.assertEqual(denied.audit[0].outcome, 'denied')
        with self.assertRaises(RuntimeError):
            denied.execute('note', {})
        allowed = AgentSession(ToolRunner(tools, ['write']))
        allowed.execute('note', {'body': 'secret'})
        self.assertEqual(calls, ['secret'])
        self.assertEqual(allowed.audit[0].outcome, 'succeeded')
        self.assertNotIn('secret', repr(allowed.audit))

    def test_failure(self):
        session = AgentSession(ToolRunner({'bad': Tool('read', lambda: 1/0)}, ['read']))
        with self.assertRaises(ZeroDivisionError):
            session.execute('bad', {})
        self.assertEqual(session.audit[0].outcome, 'failed')
