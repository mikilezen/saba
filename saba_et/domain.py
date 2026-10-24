"""Small domain models shared by every channel adapter."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    last_checked: date


@dataclass(frozen=True)
class Service:
    service_id: str
    name_am: str
    summary_am: str
    documents_am: tuple[str, ...]
    fee_etb: int | None
    source: Source


@dataclass(frozen=True)
class OutgoingMessage:
    text: str
    buttons: tuple[tuple[str, ...], ...] = ()
