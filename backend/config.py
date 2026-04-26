import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.1

BASE_DIR = Path(__file__).parent

# On Vercel only /tmp is writable; locally use the project directory.
_on_vercel = bool(os.getenv("VERCEL"))
# Source policy PDFs (shipped in repo). Uploaded replacements go to /tmp on Vercel.
POLICY_DOCS_PATH = str(BASE_DIR / "data" / "sample_policies")
POLICY_UPLOAD_PATH = os.getenv("POLICY_UPLOAD_PATH", "/tmp/policies" if _on_vercel else str(BASE_DIR / "data" / "sample_policies"))

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_TOP_K = 4

EXTRACTION_MIN_CONFIDENCE = 0.5
FRAUD_HIGH_RISK_THRESHOLD = 0.8
AUTO_APPROVE_MIN_CONFIDENCE = 0.85

# PDF ingestion limits — keeps prompts within Groq's free-tier TPM budget.
# Claim forms put all key fields on page 1-2; extra pages are attachments/T&Cs.
MAX_PDF_PAGES = 3
MAX_PDF_CHARS = 4000

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not set. Get one free at https://console.groq.com "
        "and add to backend/.env as GROQ_API_KEY=..."
    )
