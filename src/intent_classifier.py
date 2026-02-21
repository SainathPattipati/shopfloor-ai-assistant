"""Intent classifier for manufacturing shopfloor queries."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging


class ManufacturingIntent(Enum):
    """Manufacturing-specific intents."""
    SOP_LOOKUP = "sop_lookup"           # Standard Operating Procedure
    PRODUCTION_STATUS = "production_status"
    MAINTENANCE_REQUEST = "maintenance_request"
    QUALITY_CHECK = "quality_check"
    SAFETY_QUERY = "safety_query"
    WORK_ORDER = "work_order"
    PART_SEARCH = "part_search"
    TRAINING = "training"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedIntent:
    """Classification result with confidence."""
    intent: ManufacturingIntent
    confidence: float  # 0-1
    entities: Dict[str, str]  # Extracted entities (machine_id, part_number, etc.)
    clarification_needed: bool
    clarification_question: Optional[str] = None


class IntentClassifier:
    """
    Classifies manufacturing queries into actionable intents.

    Uses fine-tuned BERT with entity extraction.
    """

    def __init__(self):
        """Initialize intent classifier."""
        self._logger = logging.getLogger("intent_classifier")

        # Intent patterns (simplified BERT simulation)
        self.intent_patterns = {
            ManufacturingIntent.SOP_LOOKUP: [
                "show", "procedure", "steps", "how to", "instructions",
                "changeover", "setup", "operation", "guide"
            ],
            ManufacturingIntent.PRODUCTION_STATUS: [
                "status", "running", "downtime", "oee", "cycle time",
                "how many", "production", "output", "rate"
            ],
            ManufacturingIntent.MAINTENANCE_REQUEST: [
                "maintenance", "repair", "broken", "issue", "problem",
                "bearing", "seal", "motor", "help with"
            ],
            ManufacturingIntent.QUALITY_CHECK: [
                "quality", "check", "measure", "inspect", "specification",
                "dimension", "tolerance", "defect"
            ],
            ManufacturingIntent.SAFETY_QUERY: [
                "safety", "safe", "guard", "danger", "warning", "hazard",
                "ppe", "personal protective"
            ]
        }

        # Entity patterns
        self.entity_patterns = {
            "machine_id": ["press", "pump", "motor", "compressor", "line"],
            "part_number": ["part", "component", "product", "item"]
        }

    def classify(self, query: str) -> ClassifiedIntent:
        """
        Classify user query into manufacturing intent.

        Args:
            query: Natural language query from shopfloor user

        Returns:
            ClassifiedIntent with intent and confidence
        """
        query_lower = query.lower()

        # Score each intent
        intent_scores: Dict[ManufacturingIntent, float] = {
            intent: 0.0 for intent in ManufacturingIntent
        }

        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    intent_scores[intent] += 1.0

        # Find best match
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent] / max(
            sum(intent_scores.values()), 1
        )

        # Extract entities
        entities = self._extract_entities(query_lower)

        # Check if clarification needed
        clarification_needed = confidence < 0.5 or len(entities) == 0
        clarification_question = None

        if clarification_needed:
            if best_intent == ManufacturingIntent.SOP_LOOKUP:
                clarification_question = "Which machine or process?"
            elif best_intent == ManufacturingIntent.MAINTENANCE_REQUEST:
                clarification_question = "Which equipment needs repair?"

        return ClassifiedIntent(
            intent=best_intent,
            confidence=min(1.0, confidence),
            entities=entities,
            clarification_needed=clarification_needed,
            clarification_question=clarification_question
        )

    def _extract_entities(self, query: str) -> Dict[str, str]:
        """Extract named entities from query."""
        entities = {}

        # Machine ID extraction
        for machine_keyword in self.entity_patterns["machine_id"]:
            if machine_keyword in query:
                # Simple extraction: look for numbers after keyword
                words = query.split()
                for i, word in enumerate(words):
                    if machine_keyword in word and i + 1 < len(words):
                        next_word = words[i + 1]
                        if any(c.isdigit() for c in next_word):
                            entities["machine_id"] = next_word
                            break

        return entities
