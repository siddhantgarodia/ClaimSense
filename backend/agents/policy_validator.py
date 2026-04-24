"""
Policy validation agent: retrieves relevant policy chunks from ChromaDB
and asks Gemini to validate the claim against them.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_groq import ChatGroq

from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from schemas.claim import ClaimExtraction, PolicyValidation
from rag.retriever import retrieve_policy_context

_BACKOFF_DELAYS = [5]

def _invoke_with_backoff(fn, *args, **kwargs):
    for delay in _BACKOFF_DELAYS:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"[Validator] Rate limit — waiting {delay}s...")
                time.sleep(delay)
            else:
                raise
    return fn(*args, **kwargs)

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "validate.txt"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def validate_against_policy(extraction: ClaimExtraction) -> PolicyValidation:
    """
    Validates claim against policy documents retrieved via RAG.
    """
    query = f"{extraction.claim_type} insurance coverage {extraction.incident_description[:200]}"
    chunks = retrieve_policy_context(query, extraction.claim_type)

    if not chunks:
        return PolicyValidation(
            policy_found=False,
            policy_active=False,
            coverage_applies=False,
            max_coverage_amount=None,
            exclusions_triggered=[],
            validation_notes="No relevant policy documents found in the database.",
            validation_confidence=0.0,
        )

    policy_context = "\n\n".join(
        f"[Source: {c['source_file']}]\n{c['content']}" for c in chunks
    )

    prompt_template = _load_prompt()
    prompt = prompt_template.format(
        policy_context=policy_context,
        claimant_name=extraction.claimant_name,
        policy_number=extraction.policy_number,
        claim_type=extraction.claim_type,
        incident_date=extraction.incident_date,
        claim_amount=extraction.claim_amount,
        incident_description=extraction.incident_description,
    )

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        groq_api_key=GROQ_API_KEY,
    ).with_structured_output(PolicyValidation)

    try:
        return _invoke_with_backoff(llm.invoke, prompt)
    except Exception as e:
        print(f"[Validator] LLM call failed: {e}")
        return PolicyValidation(
            policy_found=False,
            policy_active=False,
            coverage_applies=False,
            max_coverage_amount=None,
            exclusions_triggered=[],
            validation_notes=f"Validation failed due to error: {str(e)[:100]}",
            validation_confidence=0.0,
        )
