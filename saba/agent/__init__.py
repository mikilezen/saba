"""Agent core module."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from saba.agent.context import ContextBuilder
    from saba.agent.hook import (
        AgentHook,
        AgentHookContext,
        AgentRunHookContext,
        AgentTurnHookContext,
        AgentTurnHookFactory,
        CompositeHook,
    )
    from saba.agent.loop import AgentLoop
    from saba.agent.memory import MemoryStore
    from saba.agent.skills import SkillsLoader
    from saba.agent.subagent import SubagentManager


_EXPORTS = {
    "AgentHook": "saba.agent.hook",
    "AgentHookContext": "saba.agent.hook",
    "AgentRunHookContext": "saba.agent.hook",
    "AgentTurnHookContext": "saba.agent.hook",
    "AgentTurnHookFactory": "saba.agent.hook",
    "AgentLoop": "saba.agent.loop",
    "CompositeHook": "saba.agent.hook",
    "ContextBuilder": "saba.agent.context",
    "MemoryStore": "saba.agent.memory",
    "SkillsLoader": "saba.agent.skills",
    "SubagentManager": "saba.agent.subagent",
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
    "AgentHook",
    "AgentHookContext",
    "AgentRunHookContext",
    "AgentTurnHookContext",
    "AgentTurnHookFactory",
    "AgentLoop",
    "CompositeHook",
    "ContextBuilder",
    "MemoryStore",
    "SkillsLoader",
    "SubagentManager",
]
