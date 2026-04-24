"""
LangGraph orchestration: defines the 5-node claim processing pipeline with
confidence-gated conditional edges. Exports run_claim_pipeline().
"""
import sys
from pathlib import Path
from typing import TypedDict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from langgraph.graph import StateGraph, END

from schemas.claim import (
    ClaimExtraction,
    PolicyValidation,
    FraudAssessment,
    PayoutEstimate,
    RoutingDecision,
    ClaimProcessingResult,
)
from agents.extractor import extract_claim_data
from agents.policy_validator import validate_against_policy
from agents.fraud_checker import assess_fraud
from agents.estimator import estimate_payout
from agents.router import make_routing_decision
from config import EXTRACTION_MIN_CONFIDENCE, FRAUD_HIGH_RISK_THRESHOLD


class ClaimState(TypedDict):
    claim_id: str
    pdf_text: str
    extraction: Optional[ClaimExtraction]
    policy_validation: Optional[PolicyValidation]
    fraud_assessment: Optional[FraudAssessment]
    payout_estimate: Optional[PayoutEstimate]
    routing_decision: Optional[RoutingDecision]
    log: list[str]
    error: Optional[str]


# --- Node functions ---

def extract_node(state: ClaimState) -> ClaimState:
    state["log"].append("Starting claim data extraction...")
    try:
        state["extraction"] = extract_claim_data(state["pdf_text"])
        conf = state["extraction"].extraction_confidence
        state["log"].append(
            f"Extraction complete. Confidence: {conf:.0%}. "
            f"Claimant: {state['extraction'].claimant_name}, "
            f"Amount: INR {state['extraction'].claim_amount:,.0f}"
        )
    except Exception as e:
        state["error"] = f"Extraction failed: {e}"
        state["log"].append(state["error"])
    return state


def validate_node(state: ClaimState) -> ClaimState:
    state["log"].append("Validating claim against policy documents...")
    try:
        state["policy_validation"] = validate_against_policy(state["extraction"])
        v = state["policy_validation"]
        state["log"].append(
            f"Policy validation complete. Coverage applies: {v.coverage_applies}. "
            f"Confidence: {v.validation_confidence:.0%}. Notes: {v.validation_notes[:80]}"
        )
    except Exception as e:
        err = f"Policy validation failed: {e}"
        state["log"].append(err)
        state["error"] = err
    return state


def fraud_node(state: ClaimState) -> ClaimState:
    state["log"].append("Running fraud detection (rules + LLM)...")
    try:
        extraction = state["extraction"]
        validation = state["policy_validation"]
        if extraction is None:
            raise ValueError("No extraction data available for fraud check")
        if validation is None:
            from schemas.claim import PolicyValidation as PV
            validation = PV(
                policy_found=False, policy_active=False, coverage_applies=False,
                exclusions_triggered=[], validation_notes="Skipped", validation_confidence=0.0
            )
        state["fraud_assessment"] = assess_fraud(extraction, validation)
        f = state["fraud_assessment"]
        state["log"].append(
            f"Fraud assessment complete. Risk score: {f.risk_score:.0%}. "
            f"Rule flags: {len(f.rule_flags)}. LLM concerns: {len(f.llm_concerns)}. "
            f"Recommendation: {f.recommendation}"
        )
    except Exception as e:
        err = f"Fraud assessment failed: {e}"
        state["log"].append(err)
        state["error"] = err
    return state


def estimate_node(state: ClaimState) -> ClaimState:
    state["log"].append("Estimating payout amount...")
    try:
        state["payout_estimate"] = estimate_payout(
            state["extraction"],
            state["policy_validation"],
        )
        est = state["payout_estimate"]
        state["log"].append(
            f"Payout estimate: INR {est.estimated_amount:,.0f} "
            f"(range: {est.min_amount:,.0f} - {est.max_amount:,.0f})"
        )
    except Exception as e:
        err = f"Payout estimation failed: {e}"
        state["log"].append(err)
        state["error"] = err
    return state


def route_node(state: ClaimState) -> ClaimState:
    state["log"].append("Making final routing decision...")
    try:
        state["routing_decision"] = make_routing_decision(
            state["extraction"],
            state["policy_validation"],
            state["fraud_assessment"],
            state["payout_estimate"],
        )
        rd = state["routing_decision"]
        state["log"].append(
            f"Decision: {rd.decision.upper()} (confidence: {rd.confidence:.0%}). "
            f"Reason: {rd.reasoning[:100]}"
        )
    except Exception as e:
        err = f"Routing failed: {e}"
        state["log"].append(err)
        state["routing_decision"] = RoutingDecision(
            decision="human_review",
            confidence=0.0,
            reasoning=f"Routing error — defaulting to human review. Error: {str(e)[:100]}",
        )
    return state


# --- Conditional edge routers ---

def after_extract(state: ClaimState) -> str:
    """Skip to routing if extraction confidence is too low or extraction failed."""
    extraction = state.get("extraction")
    if extraction is None or extraction.extraction_confidence < EXTRACTION_MIN_CONFIDENCE:
        state["log"].append(
            f"Low extraction confidence — skipping validation, fraud, estimate. Going to route."
        )
        return "route"
    return "validate"


def after_fraud(state: ClaimState) -> str:
    """Skip payout estimation if fraud risk is very high."""
    fraud = state.get("fraud_assessment")
    if fraud and fraud.risk_score >= FRAUD_HIGH_RISK_THRESHOLD:
        state["log"].append(
            f"High fraud risk ({fraud.risk_score:.0%}) — skipping payout estimation. Going to route."
        )
        return "route"
    return "estimate"


# --- Build graph ---

def _build_graph():
    workflow = StateGraph(ClaimState)

    workflow.add_node("extract", extract_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("fraud", fraud_node)
    workflow.add_node("estimate", estimate_node)
    workflow.add_node("route", route_node)

    workflow.set_entry_point("extract")

    workflow.add_conditional_edges(
        "extract",
        after_extract,
        {"validate": "validate", "route": "route"},
    )
    workflow.add_edge("validate", "fraud")
    workflow.add_conditional_edges(
        "fraud",
        after_fraud,
        {"estimate": "estimate", "route": "route"},
    )
    workflow.add_edge("estimate", "route")
    workflow.add_edge("route", END)

    return workflow.compile()


graph = _build_graph()


# --- Public API ---

def run_claim_pipeline(pdf_text: str, claim_id: str) -> ClaimProcessingResult:
    """Runs the full 5-agent pipeline and returns a ClaimProcessingResult."""
    initial_state: ClaimState = {
        "claim_id": claim_id,
        "pdf_text": pdf_text,
        "extraction": None,
        "policy_validation": None,
        "fraud_assessment": None,
        "payout_estimate": None,
        "routing_decision": None,
        "log": [],
        "error": None,
    }

    final_state = graph.invoke(initial_state)

    # routing_decision must always be present
    routing = final_state.get("routing_decision") or RoutingDecision(
        decision="human_review",
        confidence=0.0,
        reasoning="Pipeline did not produce a routing decision. Manual review required.",
    )

    return ClaimProcessingResult(
        claim_id=claim_id,
        extraction=final_state.get("extraction"),
        policy_validation=final_state.get("policy_validation"),
        fraud_assessment=final_state.get("fraud_assessment"),
        payout_estimate=final_state.get("payout_estimate"),
        routing_decision=routing,
        processing_log=final_state.get("log", []),
        error=final_state.get("error"),
    )
