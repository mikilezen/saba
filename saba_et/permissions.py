"""Action policy: classify request risk and gate external side effects."""

from dataclasses import dataclass
from enum import StrEnum
import re


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RiskAssessment:
    level: RiskLevel
    reason: str
    requires_confirmation: bool


class ApprovalPolicy:
    _AUTO_APPROVED_READS = {"service_catalog_search", "web_search"}
    _ALWAYS_CONFIRM = {"payment", "phone_call", "submit_form", "fayda_authentication"}
    _HIGH_RISK_INTENT = re.compile(
        r"\b(make a call|call (?:the office|them|this number)|dial|"
        r"pay (?:for me|the fee|this|now)|make (?:a )?payment|"
        r"submit (?:the |my )?(?:form|application)|file (?:the |my )?application|"
        r"book (?:it|an appointment) for me|log in for me|authenticate for me)\b"
        r"|(?<!\w)(?:ደውል|ደውሉ|ክፈል|ክፈሉ)(?!\w)"
        r"|(?<!\w)(?:bilbili|bilbilaa|kaffali|kaffalaa)(?!\w)"
        r"|(?<!\w)(?:ደውል|ደውሉ|ክፈሉ|ኣእትዉ)(?!\w)",
        re.IGNORECASE,
    )
    _MEDIUM_RISK_INTENT = re.compile(
        r"\b(prepare|draft|fill in|fill out|complete) (?:the |my )?(?:form|application)\b"
        r"|(?<!\w)(?:አዘጋጅ|አዘጋጁ|ሙላ|ሙሉ)(?!\w).{0,24}(?:ቅጽ|ማመልከቻ)"
        r"|(?<!\w)(?:qopheessi|guuti)(?!\w).{0,24}(?:unka|gaaffii)",
        re.IGNORECASE,
    )

    def can_run_automatically(self, action: str) -> bool:
        return action in self._AUTO_APPROVED_READS

    def requires_fresh_confirmation(self, action: str) -> bool:
        return action in self._ALWAYS_CONFIRM

    def assess_request(self, request: str) -> RiskAssessment:
        """Classify the requested intent; the model cannot lower this risk."""
        if self._HIGH_RISK_INTENT.search(request):
            return RiskAssessment(
                RiskLevel.HIGH,
                "The request could place a call, move money, submit a form, or access an account.",
                True,
            )
        if self._MEDIUM_RISK_INTENT.search(request):
            return RiskAssessment(
                RiskLevel.MEDIUM,
                "The request prepares information for a person to review before they submit it.",
                False,
            )
        return RiskAssessment(
            RiskLevel.LOW,
            "The enabled actions are read-only local lookup and public-source search.",
            False,
        )
