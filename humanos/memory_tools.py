"""Explicit capabilities for local memory; no implicit grants."""
from .permissions import Tool, ToolRunner


def memory_runner(memory, grants=()):
    def add(body):
        if type(body) is not str:
            raise ValueError('Expected text')
        return memory.add(body)

    def search(query):
        if type(query) is not str or not query.strip() or len(query) > 1000:
            raise ValueError('Expected nonempty query of at most 1000 characters')
        return memory.search(query)

    def delete(note_id):
        if type(note_id) is not int or not 1 <= note_id <= 2**63 - 1:
            raise ValueError('Invalid note ID')
        return memory.delete(note_id)

    return ToolRunner({'memory.add': Tool('memory.write', add),
                       'memory.search': Tool('memory.read', search),
                       'memory.delete': Tool('memory.delete', delete)}, grants)
