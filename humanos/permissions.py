"""Explicit per-session capabilities for trusted, registered tools."""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable

@dataclass(frozen=True)
class Tool:
    capability: str
    handler: Callable

class ToolRunner:
    def __init__(self, tools: dict[str, Tool], grants=()):
        self._tools = MappingProxyType(dict(tools))
        self._grants = frozenset(grants)

    def execute(self, name: str, arguments: dict):
        if not isinstance(name, str) or name not in self._tools:
            raise PermissionError('Unknown tool')
        tool = self._tools[name]
        if tool.capability not in self._grants:
            raise PermissionError('Capability not granted')
        if type(arguments) is not dict or any(type(k) is not str for k in arguments):
            raise ValueError('Arguments must be an object with string keys')
        return tool.handler(**arguments)
