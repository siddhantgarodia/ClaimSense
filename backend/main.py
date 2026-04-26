"""
FastAPI application for ClaimSense. Exposes:
  GET  /health              - liveness check
  GET  /policies            - list ingested policies and chunk counts
  POST /process-claim       - multipart PDF upload → ClaimProcessingResult JSON
  POST /upload-policy       - upload + ingest a new policy PDF
  GET  /samples/*           - static serving of sample claim PDFs for the UI
"""
import asyncio
import io
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

from config import BASE_DIR, LLM_MODEL, MAX_PDF_CHARS, MAX_PDF_PAGES, POLICY_DOCS_PATH, POLICY_UPLOAD_PATH
from graph import run_claim_pipeline
from rag.ingest_policies import ingest_all_policies, ingest_single_policy
from schemas.claim import ClaimProcessingResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="ClaimSense API", version="1.0.0")

# Serve sample claim PDFs so the test-cases UI can submit them directly
_samples_dir = BASE_DIR / "data" / "sample_claims"
if _samples_dir.exists():
    app.mount("/samples", StaticFiles(directory=str(_samples_dir)), name="samples")

_executor = ThreadPoolExecutor(max_workers=2)
PIPELINE_TIMEOUT = 55  # seconds — stays under typical 60s proxy timeout

_extra_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"] + _extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_TEXT_LENGTH = 50

_CLAIM_KEYWORDS = ["claimant", "claim form", "amount claimed", "incident date", "damage"]
_POLICY_KEYWORDS = ["policy type", "covered events", "sum insured", "premium", "exclusions", "policy series"]

POLICY_TYPE_ICONS = {
    "motor": "🚗",
    "health": "🏥",
    "home": "🏠",
    "life": "💖",
}


def _reject_non_claim(text: str) -> None:
    lower = text.lower()
    claim_hits = sum(1 for kw in _CLAIM_KEYWORDS if kw in lower)
    policy_hits = sum(1 for kw in _POLICY_KEYWORDS if kw in lower)
    if policy_hits > claim_hits:
        raise HTTPException(
            status_code=400,
            detail=(
                "This looks like a policy document, not a claim form. "
                "Please upload a completed insurance claim form PDF. "
                "Use the Test Cases panel to run pre-built scenarios."
            ),
        )


# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info(f"ClaimSense starting. Model: {LLM_MODEL}")
    try:
        result = ingest_all_policies()
        logger.info(f"Policy ingestion: {result or 'already done'}")
    except Exception as e:
        logger.warning(f"Policy ingestion failed on startup: {e}")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model": LLM_MODEL}


@app.get("/policies")
def list_policies():
    """Return each ingested policy type with its chunk count and source file."""
    try:
        from rag.retriever import _get_vectorstore
        vs = _get_vectorstore()
        data = vs._collection.get(include=["metadatas"])
        counts: dict[str, int] = {}
        sources: dict[str, str] = {}
        for meta in (data.get("metadatas") or []):
            pt = meta.get("policy_type", "unknown")
            counts[pt] = counts.get(pt, 0) + 1
            sources.setdefault(pt, meta.get("source_file", f"{pt}_policy.pdf"))
        policies = [
            {
                "type": k,
                "chunks": counts[k],
                "source_file": sources[k],
                "icon": POLICY_TYPE_ICONS.get(k, "📋"),
            }
            for k in sorted(counts)
        ]
        return {"policies": policies}
    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        return {"policies": []}


@app.post("/upload-policy")
async def upload_policy(
    file: UploadFile = File(...),
    policy_type: str = Form(...),
):
    """Upload a new policy PDF and ingest it into ChromaDB."""
    policy_type = policy_type.strip().lower()
    if not policy_type.isalnum():
        raise HTTPException(status_code=400, detail="Policy type must be alphanumeric (e.g. 'motor', 'health').")
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB).")

    upload_dir = Path(POLICY_UPLOAD_PATH)
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / f"{policy_type}_policy.pdf"
    save_path.write_bytes(content)
    logger.info(f"Saved policy PDF to {save_path}")

    try:
        chunks = ingest_single_policy(save_path, policy_type)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Policy saved but ingestion failed: {e}")

    return {
        "message": f"Policy '{policy_type}' uploaded and ingested successfully.",
        "chunks": chunks,
        "type": policy_type,
        "icon": POLICY_TYPE_ICONS.get(policy_type, "📋"),
    }


@app.post("/process-claim", response_model=ClaimProcessingResult)
async def process_claim(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE // (1024*1024)} MB).")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        reader = PdfReader(io.BytesIO(content))
        total_pages = len(reader.pages)
        pages = reader.pages[:MAX_PDF_PAGES]
        pdf_text = "\n".join(page.extract_text() or "" for page in pages).strip()
        if total_pages > MAX_PDF_PAGES:
            logger.info(f"PDF has {total_pages} pages; reading first {MAX_PDF_PAGES}.")
        if len(pdf_text) > MAX_PDF_CHARS:
            pdf_text = pdf_text[:MAX_PDF_CHARS]
    except Exception as e:
        logger.error(f"PDF parse error: {e}")
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}")

    if len(pdf_text) < MIN_TEXT_LENGTH:
        raise HTTPException(status_code=400, detail="PDF appears to be scanned/image-based. OCR is not supported.")

    _reject_non_claim(pdf_text)

    claim_id = str(uuid4())
    logger.info(f"Processing claim {claim_id} ({len(pdf_text)} chars, {file.filename})")

    loop = asyncio.get_event_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, lambda: run_claim_pipeline(pdf_text=pdf_text, claim_id=claim_id)),
            timeout=PIPELINE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=503,
            detail=f"Processing timed out ({PIPELINE_TIMEOUT}s). Groq rate limit likely hit — wait 60 s and retry.",
        )
    except Exception as e:
        logger.error(f"Pipeline error {claim_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Claim processing failed. Please try again.")

    logger.info(f"Claim {claim_id} → {result.routing_decision.decision}")
    return result
