"""
Routing agent: pure logic, no LLM. Makes the final claim decision based on
confidence scores, fraud risk, and policy validation results.
"""
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import EXTRACTION_MIN_CONFIDENCE, FRAUD_HIGH_RISK_THRESHOLD, AUTO_APPROVE_MIN_CONFIDENCE
from schemas.claim import ClaimExtraction, PolicyValidation, FraudAssessment, PayoutEstimate, RoutingDecision


def make_routing_decision(
    extraction: Optional[ClaimExtraction],
    validation: Optional[PolicyValidation],
    fraud: Optional[FraudAssessment],
    estimate: Optional[PayoutEstimate],
) -> RoutingDecision:
    """
    Applies confidence-gated routing logic to determine final claim disposition.
    """
    # No extraction at all — cannot process
    if extraction is None:
        return RoutingDecision(
            decision="human_review",
            confidence=0.0,
            reasoning="Claim data could not be extracted from the document. Manual review required.",
        )

    # Low extraction confidence — humans must verify the data
    if extraction.extraction_confidence < EXTRACTION_MIN_CONFIDENCE:
        return RoutingDecision(
            decision="human_review",
            confidence=extraction.extraction_confidence,
            reasoning=(
                f"Extraction confidence is too low ({extraction.extraction_confidence:.0%}). "
                "The document may be unclear or missing required fields. Manual verification needed."
            ),
        )

    # High fraud risk — reject or flag for investigation
    if fraud and fraud.risk_score >= FRAUD_HIGH_RISK_THRESHOLD:
        return RoutingDecision(
            decision="reject",
            confidence=fraud.risk_score,
            reasoning=(
                f"High fraud risk score ({fraud.risk_score:.0%}). "
                f"Flags: {'; '.join(fraud.rule_flags + fraud.llm_concerns)}"
            ),
        )

    # Coverage does not apply — reject
    if validation and not validation.coverage_applies:
        return RoutingDecision(
            decision="reject",
            confidence=validation.validation_confidence,
            reasoning=(
                f"Policy coverage does not apply to this claim. "
                f"Notes: {validation.validation_notes}"
            ),
        )

    # Policy not found or not active — human review
    if validation and (not validation.policy_found or not validation.policy_active):
        return RoutingDecision(
            decision="human_review",
            confidence=validation.validation_confidence,
            reasoning=(
                "Policy could not be verified as active. "
                f"Notes: {validation.validation_notes}"
            ),
        )

    # Medium fraud risk — send to human
    if fraud and fraud.risk_score >= 0.3:
        return RoutingDecision(
            decision="human_review",
            confidence=1.0 - fraud.risk_score,
            reasoning=(
                f"Moderate fraud risk ({fraud.risk_score:.0%}) requires human verification. "
                f"Concerns: {'; '.join(fraud.rule_flags + fraud.llm_concerns)}"
            ),
        )

    # All signals green — auto approve
    extraction_ok = extraction.extraction_confidence >= AUTO_APPROVE_MIN_CONFIDENCE
    validation_ok = validation is not None and validation.validation_confidence >= AUTO_APPROVE_MIN_CONFIDENCE
    fraud_ok = fraud is None or fraud.risk_score < 0.3

    if extraction_ok and validation_ok and fraud_ok:
        avg_confidence = (
            extraction.extraction_confidence + (validation.validation_confidence if validation else 0.0)
        ) / 2
        return RoutingDecision(
            decision="auto_approve",
            confidence=round(avg_confidence, 3),
            reasoning=(
                f"All checks passed. Extraction confidence: {extraction.extraction_confidence:.0%}, "
                f"Policy validation confidence: {validation.validation_confidence:.0%}, "
                f"Fraud risk: {fraud.risk_score:.0%}."
            ),
        )

    # Default: human review
    reasons = []
    if not extraction_ok:
        reasons.append(f"extraction confidence {extraction.extraction_confidence:.0%} below threshold")
    if not validation_ok:
        reasons.append(f"policy validation confidence {validation.validation_confidence if validation else 0:.0%} below threshold")
    if not fraud_ok:
        reasons.append(f"fraud risk {fraud.risk_score:.0%}")

    return RoutingDecision(
        decision="human_review",
        confidence=0.5,
        reasoning="Sent for human review: " + "; ".join(reasons) + ".",
    )
