"""Contracts for integrations; real external actions require explicit consent."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class PluginStatus(StrEnum):
    OPEN = "open"
    NEEDS_APPROVAL = "needs approval"
    NONE_FOUND = "none found"
    MOCK = "mock"


@dataclass(frozen=True)
class PluginInfo:
    name: str
    purpose: str
    connection: str
    status: PluginStatus
    fallback: str


class Plugin(Protocol):
    @property
    def info(self) -> PluginInfo: ...


class UnavailablePlugin:
    """Safe placeholder until an integration is approved and configured."""

    def __init__(self, info: PluginInfo) -> None:
        self._info = info

    @property
    def info(self) -> PluginInfo:
        return self._info


PAYMENT_PLUGIN = UnavailablePlugin(
    PluginInfo(
        name="payments",
        purpose="Provide a payment link for a verified government fee.",
        connection="No provider configured; integration requires approved credentials.",
        status=PluginStatus.MOCK,
        fallback="Show official payment instructions or direct the person to the office.",
    )
)

PHONE_PLUGIN = UnavailablePlugin(
    PluginInfo(
        name="phone",
        purpose="Call an official office when the person requests it.",
        connection="No calling provider configured.",
        status=PluginStatus.MOCK,
        fallback="Show the verified official office contact for the person to call.",
    )
)
