"""
Payout estimator agent: asks Gemini to estimate a reasonable payout range
based on the claim details and validated policy information.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

_BACKOFF_DELAYS = [5]

def _invoke_with_backoff(fn, *args, **kwargs):
    for delay in _BACKOFF_DELAYS:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"[Estimator] Rate limit — waiting {delay}s...")
                time.sleep(delay)
            else:
                raise
    return fn(*args, **kwargs)

from langchain_groq import ChatGroq

from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from schemas.claim import ClaimExtraction, PolicyValidation, PayoutEstimate

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "estimate.txt"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def estimate_payout(
    extraction: ClaimExtraction,
    validation: PolicyValidation,
) -> PayoutEstimate:
    """
    Produces a conservative payout estimate within policy coverage limits.
    Falls back to a simple rule-based estimate if the LLM call fails.
    """
    prompt_template = _load_prompt()
    prompt = prompt_template.format(
        claim_amount=extraction.claim_amount,
        max_coverage_amount=validation.max_coverage_amount or "Not specified",
        damage_items=", ".join(extraction.damage_items) if extraction.damage_items else "None listed",
        exclusions_triggered=", ".join(validation.exclusions_triggered) if validation.exclusions_triggered else "None",
    )

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        groq_api_key=GROQ_API_KEY,
    ).with_structured_output(PayoutEstimate)

    try:
        return _invoke_with_backoff(llm.invoke, prompt)
    except Exception as e:
        print(f"[Estimator] LLM call failed: {e}. Using rule-based fallback.")
        # Fallback: 80% of claim amount, capped at max coverage
        cap = validation.max_coverage_amount or extraction.claim_amount
        estimated = min(extraction.claim_amount * 0.8, cap)
        return PayoutEstimate(
            estimated_amount=round(estimated, 2),
            min_amount=round(estimated * 0.7, 2),
            max_amount=round(min(extraction.claim_amount, cap), 2),
            reasoning="Estimated at 80% of claimed amount due to LLM unavailability.",
        )
