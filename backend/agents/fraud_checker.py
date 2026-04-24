"""
Fraud detection agent: hybrid approach combining hardcoded business rules
with an LLM semantic check. Final score = 0.6 * rule_score + 0.4 * llm_score.
"""
import sys
import time
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

_BACKOFF_DELAYS = [5]

def _invoke_with_backoff(fn, *args, **kwargs):
    for delay in _BACKOFF_DELAYS:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"[FraudChecker] Rate limit — waiting {delay}s...")
                time.sleep(delay)
            else:
                raise
    return fn(*args, **kwargs)

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from schemas.claim import ClaimExtraction, PolicyValidation, FraudAssessment

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "fraud.txt"


class LLMFraudOutput(BaseModel):
    concerns: list[str] = Field(default_factory=list)
    llm_risk_score: float = Field(ge=0.0, le=1.0)


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def check_rules(extraction: ClaimExtraction, validation: PolicyValidation) -> list[str]:
    """Applies hardcoded fraud detection rules. Returns list of flag strings."""
    flags = []

    # Rule 1: Claim exceeds max coverage
    if validation.max_coverage_amount and extraction.claim_amount > validation.max_coverage_amount:
        flags.append(
            f"Claim amount ({extraction.claim_amount:,.0f}) exceeds max coverage ({validation.max_coverage_amount:,.0f})"
        )

    # Rules 2 & 3: Date-based checks
    try:
        incident = date.fromisoformat(extraction.incident_date)
        if incident > date.today():
            flags.append(f"Incident date {extraction.incident_date} is in the future")
        elif (date.today() - incident).days > 90:
            flags.append(
                f"Incident reported more than 90 days after event ({(date.today() - incident).days} days)"
            )
    except ValueError:
        flags.append(f"Invalid incident date format: {extraction.incident_date}")

    # Rule 4: Exclusions triggered
    if validation.exclusions_triggered:
        flags.append(f"Policy exclusions triggered: {', '.join(validation.exclusions_triggered)}")

    # Rule 5: Suspiciously round claim amount
    if extraction.claim_amount >= 50000 and extraction.claim_amount % 10000 == 0:
        flags.append(f"Suspiciously round claim amount: INR {extraction.claim_amount:,.0f}")

    return flags


def assess_fraud(
    extraction: ClaimExtraction,
    validation: PolicyValidation,
) -> FraudAssessment:
    """Combines rule-based and LLM-based fraud signals into a single FraudAssessment."""
    rule_flags = check_rules(extraction, validation)
    rule_score = min(1.0, len(rule_flags) * 0.3)

    # LLM semantic check
    prompt_template = _load_prompt()
    prompt = prompt_template.format(
        incident_description=extraction.incident_description,
        damage_items=", ".join(extraction.damage_items) if extraction.damage_items else "None listed",
        claim_amount=extraction.claim_amount,
    )

    llm_concerns: list[str] = []
    llm_score = 0.0

    try:
        llm = ChatGroq(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            groq_api_key=GROQ_API_KEY,
        ).with_structured_output(LLMFraudOutput)
        llm_output: LLMFraudOutput = _invoke_with_backoff(llm.invoke, prompt)
        llm_concerns = llm_output.concerns
        llm_score = llm_output.llm_risk_score
    except Exception as e:
        print(f"[FraudChecker] LLM call failed: {e}")
        llm_concerns = []
        llm_score = 0.0

    final_score = round(0.6 * rule_score + 0.4 * llm_score, 3)

    if final_score < 0.3:
        recommendation = "proceed"
    elif final_score < 0.7:
        recommendation = "review"
    else:
        recommendation = "investigate"

    return FraudAssessment(
        risk_score=final_score,
        rule_flags=rule_flags,
        llm_concerns=llm_concerns,
        recommendation=recommendation,
    )
