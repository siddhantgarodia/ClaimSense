"""
Policy ingestion — in-memory text store (no ChromaDB/embeddings).
Loads policy PDFs into a dict at startup; identical public API to the old ChromaDB version.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pypdf import PdfReader

from config import POLICY_DOCS_PATH, CHUNK_SIZE

# policy_type -> full extracted text
_policy_text: dict[str, str] = {}


def _extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def ingest_all_policies(force_reingest: bool = False) -> dict:
    """Load all policy PDFs from POLICY_DOCS_PATH into memory."""
    policy_dir = Path(POLICY_DOCS_PATH)
    if not policy_dir.exists():
        return {}
    results = {}
    for pdf_path in sorted(policy_dir.glob("*.pdf")):
        policy_type = pdf_path.stem.replace("_policy", "")
        if policy_type not in _policy_text or force_reingest:
            text = _extract_text(pdf_path)
            if text:
                _policy_text[policy_type] = text
                results[policy_type] = max(1, len(text) // CHUNK_SIZE)
                print(f"[RAG] Loaded {pdf_path.name}: {len(text)} chars (type={policy_type})")
    return results


def ingest_single_policy(pdf_path: Path, policy_type: str) -> int:
    """Load (or reload) a single policy PDF."""
    text = _extract_text(pdf_path)
    if not text:
        raise ValueError(f"No text extracted from {pdf_path.name}")
    _policy_text[policy_type] = text
    chunk_count = max(1, len(text) // CHUNK_SIZE)
    print(f"[RAG] Loaded {pdf_path.name}: {len(text)} chars, ~{chunk_count} chunks")
    return chunk_count


if __name__ == "__main__":
    result = ingest_all_policies(force_reingest=True)
    print(f"Ingestion complete: {result}")
