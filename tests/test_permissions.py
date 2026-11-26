import unittest
from unittest.mock import Mock
from humanos.permissions import Tool, ToolRunner

class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.handler = Mock(return_value='ok')
        self.tools = {'read': Tool('notes.read', self.handler)}

    def test_default_denial(self):
        with self.assertRaises(PermissionError):
            ToolRunner(self.tools).execute('read', {})
        self.handler.assert_not_called()

    def test_explicit_grant(self):
        self.assertEqual(ToolRunner(self.tools, ['notes.read']).execute('read', {'query':'x'}), 'ok')
        self.handler.assert_called_once_with(query='x')

    def test_unknown_tool(self):
        with self.assertRaises(PermissionError):
            ToolRunner(self.tools, ['notes.read']).execute('shell', {})
        self.handler.assert_not_called()

    def test_grants_snapshot(self):
        grants = []
        runner = ToolRunner(self.tools, grants)
        grants.append('notes.read')
        with self.assertRaises(PermissionError):
            runner.execute('read', {})

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            ToolRunner(self.tools, ['notes.read']).execute('read', [])
        self.handler.assert_not_called()
