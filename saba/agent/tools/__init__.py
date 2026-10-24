"""Public tool contracts and discovery interfaces."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from saba.agent.tools.base import Schema, Tool, ToolResult, tool_parameters
    from saba.agent.tools.context import ToolContext
    from saba.agent.tools.loader import ToolLoader
    from saba.agent.tools.registry import ToolRegistry
    from saba.agent.tools.schema import (
        ArraySchema,
        BooleanSchema,
        IntegerSchema,
        NumberSchema,
        ObjectSchema,
        StringSchema,
        tool_parameters_schema,
    )


_EXPORTS = {
    "Schema": "saba.agent.tools.base",
    "ArraySchema": "saba.agent.tools.schema",
    "BooleanSchema": "saba.agent.tools.schema",
    "IntegerSchema": "saba.agent.tools.schema",
    "NumberSchema": "saba.agent.tools.schema",
    "ObjectSchema": "saba.agent.tools.schema",
    "StringSchema": "saba.agent.tools.schema",
    "Tool": "saba.agent.tools.base",
    "ToolContext": "saba.agent.tools.context",
    "ToolLoader": "saba.agent.tools.loader",
    "ToolResult": "saba.agent.tools.base",
    "ToolRegistry": "saba.agent.tools.registry",
    "tool_parameters": "saba.agent.tools.base",
    "tool_parameters_schema": "saba.agent.tools.schema",
}


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


__all__ = [
    "Schema",
    "ArraySchema",
    "BooleanSchema",
    "IntegerSchema",
    "NumberSchema",
    "ObjectSchema",
    "StringSchema",
    "Tool",
    "ToolContext",
    "ToolLoader",
    "ToolResult",
    "ToolRegistry",
    "tool_parameters",
    "tool_parameters_schema",
]
