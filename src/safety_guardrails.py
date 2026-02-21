"""Safety guardrails preventing dangerous assistant recommendations."""

from typing import Dict, List, Optional
from enum import Enum
import logging


class SafetyLevel(Enum):
    """Safety criticality levels."""
    ALLOWED = "allowed"              # Safe to answer
    REQUIRES_CONFIRMATION = "confirmation"  # Needs human approval
    FORBIDDEN = "forbidden"          # Dangerous, refuse


class SafetyGuardrails:
    """
    Safety constraints for manufacturing assistant.

    Prevents recommendations that could cause harm.
    """

    def __init__(self):
        """Initialize safety guardrails."""
        self._logger = logging.getLogger("safety_guardrails")

        # Forbidden actions
        self.forbidden_keywords = [
            "bypass", "disable", "remove", "ignore", "override",
            "safety", "interlock", "guard", "sensor", "alarm"
        ]

        # Requires confirmation
        self.confirmation_keywords = [
            "emergency", "stop", "shutdown", "power off", "restart"
        ]

        # OSHA/ISO standards to cite
        self.safety_standards = {
            "lockout_tagout": "OSHA 1910.147 - Lockout/Tagout",
            "guards": "OSHA 1910.212 - General Requirements for Safety",
            "ppe": "OSHA 1910 Subpart I - Personal Protective Equipment",
            "emergency": "ANSI Z535.1 - Safety Color Code"
        }

    def check_safety(
        self,
        query: str,
        response: str
    ) -> tuple[SafetyLevel, Optional[str]]:
        """
        Check if response is safe to deliver.

        Args:
            query: User question
            response: Assistant's proposed response

        Returns:
            Tuple of (SafetyLevel, explanation)
        """
        response_lower = response.lower()

        # Check for forbidden content
        for keyword in self.forbidden_keywords:
            if keyword in response_lower:
                reason = f"Response contains unsafe keyword: '{keyword}'"
                self._logger.warning(f"Blocked: {reason}")
                return SafetyLevel.FORBIDDEN, reason

        # Check for emergency-level queries
        for keyword in self.confirmation_keywords:
            if keyword in response_lower:
                reason = f"Emergency action requires human confirmation"
                return SafetyLevel.REQUIRES_CONFIRMATION, reason

        return SafetyLevel.ALLOWED, None

    def sanitize_response(
        self,
        response: str,
        safety_topic: Optional[str] = None
    ) -> str:
        """
        Add safety disclaimers to response.

        Args:
            response: Original response
            safety_topic: Relevant safety topic

        Returns:
            Response with safety disclaimers
        """
        if safety_topic and safety_topic in self.safety_standards:
            standard = self.safety_standards[safety_topic]
            disclaimer = f"\n\nSafety Note: See {standard}"
            return response + disclaimer

        # Generic safety disclaimer for any response
        if any(word in response.lower() for word in ["procedure", "step", "do"]):
            disclaimer = "\n\nAlways follow established procedures and safety protocols."
            return response + disclaimer

        return response
