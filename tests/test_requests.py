import unittest
from unittest.mock import Mock
from humanos.requests import parse_request, execute_request


class RequestTests(unittest.TestCase):
    def test_dispatch(self):
        session = Mock()
        execute_request(session, '{"tool":"note","arguments":{"body":"hello"}}')
        session.execute.assert_called_once_with('note', {'body': 'hello'})

    def test_invalid_never_dispatches(self):
        session = Mock()
        for raw in ('[]', '{}', '{"tool":"a","tool":"b","arguments":{}}',
                    '{"tool":"a","arguments":{"x":NaN}}',
                    '{"tool":"a","arguments":{},"grants":["write"]}',
                    '{"tool":"a","arguments":[]}', 'x'*16385,
                    '['*2000 + ']'*2000):
            with self.subTest(raw=raw[:80]), self.assertRaises(ValueError):
                execute_request(session, raw)
        session.execute.assert_not_called()

    def test_denial_propagates(self):
        session = Mock()
        session.execute.side_effect = PermissionError('denied')
        with self.assertRaises(PermissionError):
            execute_request(session, '{"tool":"note","arguments":{}}')
