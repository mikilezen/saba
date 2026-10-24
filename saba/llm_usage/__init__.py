"""Public LLM usage records and persistence services."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from saba.llm_usage.models import LLMCallRecord
    from saba.llm_usage.service import (
        empty_usage_payload,
        get_llm_usage_store,
        llm_usage_payload,
        llm_usage_store_path,
        record_llm_call,
    )
    from saba.llm_usage.store import LLMUsageStore

_EXPORTS = {
    "LLMCallRecord": "saba.llm_usage.models",
    "LLMUsageStore": "saba.llm_usage.store",
    "empty_usage_payload": "saba.llm_usage.service",
    "get_llm_usage_store": "saba.llm_usage.service",
    "record_llm_call": "saba.llm_usage.service",
    "llm_usage_store_path": "saba.llm_usage.service",
    "llm_usage_payload": "saba.llm_usage.service",
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
    "LLMCallRecord",
    "LLMUsageStore",
    "empty_usage_payload",
    "get_llm_usage_store",
    "record_llm_call",
    "llm_usage_store_path",
    "llm_usage_payload",
]
