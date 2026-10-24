"""Message bus module for decoupled channel-agent communication."""

from saba.bus.events import InboundMessage, OutboundMessage
from saba.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
