import tempfile
import unittest
from pathlib import Path
from humanos.memory import Memory

class MemoryTests(unittest.TestCase):
    def test_persistence_search_and_delete(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.db"
            note_id = Memory(path).add("Private note")
            memory = Memory(path)
            self.assertEqual(memory.search("PRIVATE"), [{"id": note_id, "body": "Private note"}])
            self.assertEqual(memory.search("' OR 1=1 --"), [])
            self.assertTrue(memory.delete(note_id))
            self.assertFalse(memory.delete(note_id))
            self.assertEqual(Memory(path).search(), [])

    def test_blank_note(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                Memory(Path(directory) / "memory.db").add(" ")
