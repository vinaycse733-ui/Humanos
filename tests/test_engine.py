import unittest
from unittest.mock import patch
from humanos.engine import ask

class EngineTests(unittest.TestCase):
    def test_empty_prompt(self):
        with self.assertRaises(ValueError):
            ask(" ")

    @patch("humanos.engine.http.client.HTTPConnection")
    def test_local_response(self, connection):
        response = connection.return_value.getresponse.return_value
        response.status = 200
        response.read.return_value = b'{"response":"hello"}'
        self.assertEqual(ask("hi"), "hello")
        connection.assert_called_once_with("127.0.0.1", 11434, timeout=120)

    @patch("humanos.engine.http.client.HTTPConnection")
    def test_http_error(self, connection):
        connection.return_value.getresponse.return_value.status = 503
        with self.assertRaises(RuntimeError):
            ask("hi")
