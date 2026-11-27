import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from humanos.agent import AgentSession
from humanos.permissions import Tool, ToolRunner

class ConcurrencyTests(unittest.TestCase):
    def test_budget(self):
        session = AgentSession(ToolRunner({'read': Tool('read', lambda: 1)}, ['read']), limit=3)
        barrier = Barrier(16)
        def run(_):
            barrier.wait(timeout=10)
            try:
                return session.execute('read', {})
            except RuntimeError:
                return 0
        with ThreadPoolExecutor(max_workers=16) as pool:
            self.assertEqual(sum(pool.map(run, range(16))), 3)
        self.assertEqual([e.sequence for e in session.audit], [1, 2, 3])
        self.assertTrue(all(e.outcome == 'succeeded' for e in session.audit))
