from pydantic import BaseModel, Field
from typing import Literal, Optional


class ClaimExtraction(BaseModel):
    """Data extracted from the uploaded claim document."""
    claimant_name: str = Field(description="Full name of person filing claim")
    policy_number: str = Field(description="Policy number, e.g., POL-MOT-12345")
    claim_type: Literal["motor", "health", "home", "life", "other"]
    incident_date: str = Field(description="Date of incident in YYYY-MM-DD format")
    claim_amount: float = Field(ge=0.0, description="Amount claimed in INR")
    incident_description: str
    damage_items: list[str] = Field(default_factory=list)
    extraction_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Self-reported confidence: 1.0 if all fields clearly present, lower if inferred"
    )


class PolicyValidation(BaseModel):
    """Result of validating claim against retrieved policy documents."""
    policy_found: bool
    policy_active: bool
    coverage_applies: bool
    max_coverage_amount: Optional[float] = None
    exclusions_triggered: list[str] = Field(default_factory=list)
    validation_notes: str
    validation_confidence: float = Field(ge=0.0, le=1.0)


class FraudAssessment(BaseModel):
    """Fraud risk evaluation combining rules + LLM signals."""
    risk_score: float = Field(ge=0.0, le=1.0, description="0=no risk, 1=certain fraud")
    rule_flags: list[str] = Field(default_factory=list)
    llm_concerns: list[str] = Field(default_factory=list)
    recommendation: Literal["proceed", "review", "investigate"]


class PayoutEstimate(BaseModel):
    estimated_amount: float
    min_amount: float
    max_amount: float
    reasoning: str


class RoutingDecision(BaseModel):
    decision: Literal["auto_approve", "human_review", "reject"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class ClaimProcessingResult(BaseModel):
    """Complete result returned to the frontend."""
    claim_id: str
    extraction: Optional[ClaimExtraction] = None
    policy_validation: Optional[PolicyValidation] = None
    fraud_assessment: Optional[FraudAssessment] = None
    payout_estimate: Optional[PayoutEstimate] = None
    routing_decision: RoutingDecision
    processing_log: list[str] = Field(default_factory=list)
    error: Optional[str] = None
