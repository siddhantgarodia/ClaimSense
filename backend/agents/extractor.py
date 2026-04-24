"""
Extraction agent: uses Gemini with structured output to parse claim PDF text
into a ClaimExtraction Pydantic model.

Three-tier fallback:
  1. with_structured_output (function-calling mode, ideal)
  2. Manual JSON parse of raw LLM text (handles non-conforming responses)
  3. Raises RuntimeError so the graph logs the real error

429 rate-limit errors trigger an automatic wait-and-retry with backoff.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_groq import ChatGroq

from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from schemas.claim import ClaimExtraction

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extract.txt"

# One 5-second pause then a final attempt; keeps total wait well under the 55s pipeline timeout
_BACKOFF_DELAYS = [5]


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_llm() -> ChatGroq:
    return ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        groq_api_key=GROQ_API_KEY,
    )


def _is_rate_limit(exc: Exception) -> bool:
    return "429" in str(exc) or "quota" in str(exc).lower() or "rate" in str(exc).lower()


def _invoke_with_backoff(fn, *args, **kwargs):
    """Call fn(*args, **kwargs), retrying on 429 with exponential backoff."""
    for delay in _BACKOFF_DELAYS:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if _is_rate_limit(e):
                print(f"[Extractor] Rate limit hit — waiting {delay}s before retry...")
                time.sleep(delay)
            else:
                raise
    # Final attempt after last backoff
    return fn(*args, **kwargs)


def _parse_json_from_text(text: str) -> ClaimExtraction:
    """Extract the first JSON object from free-form LLM text and parse it."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response: {text[:300]}")
    data = json.loads(match.group())
    return ClaimExtraction(**data)


def extract_claim_data(pdf_text: str) -> ClaimExtraction:
    """
    Extracts structured claim data from raw PDF text.
    Raises RuntimeError if all attempts fail so the caller can log the real error.
    """
    base_llm = _build_llm()
    prompt_template = _load_prompt()
    prompt = prompt_template.format(pdf_text=pdf_text)

    # --- Attempt 1: with_structured_output (function-calling mode) ---
    err1 = ""
    try:
        chain = base_llm.with_structured_output(ClaimExtraction, include_raw=True)
        raw_result = _invoke_with_backoff(chain.invoke, prompt)
        if raw_result.get("parsed") is not None:
            return raw_result["parsed"]
        raw_content = getattr(raw_result.get("raw"), "content", "")
        if raw_content:
            print("[Extractor] Structured parse failed; trying manual JSON parse of raw response.")
            return _parse_json_from_text(raw_content)
    except Exception as e:
        err1 = str(e)
        print(f"[Extractor] Attempt 1 (structured output) failed: {err1[:150]}")

    # --- Attempt 2: plain text call + manual JSON parse ---
    err2 = ""
    try:
        schema_hint = json.dumps(ClaimExtraction.model_json_schema(), indent=2)
        json_prompt = (
            f"{prompt}\n\n"
            "Respond with ONLY a valid JSON object — no markdown, no explanation, no extra text. "
            f"The JSON must match this schema:\n{schema_hint}"
        )
        response = _invoke_with_backoff(base_llm.invoke, json_prompt)
        text = response.content if hasattr(response, "content") else str(response)
        return _parse_json_from_text(text)
    except Exception as e:
        err2 = str(e)
        print(f"[Extractor] Attempt 2 (JSON fallback) failed: {err2[:150]}")

    # Surface a clear message for 429 so the user knows what to do
    combined = f"{err1} {err2}"
    if _is_rate_limit(Exception(combined)):
        raise RuntimeError(
            "Gemini API rate limit exceeded (429). "
            "The free tier allows ~15 requests/minute. "
            "Please wait 60 seconds and try again."
        )

    raise RuntimeError(
        f"Extraction failed after 2 attempts. "
        f"Attempt 1: {err1[:120]} | Attempt 2: {err2[:120]}"
    )
