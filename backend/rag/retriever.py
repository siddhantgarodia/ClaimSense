"""
Policy retrieval — returns text chunks from the in-memory policy store.
Same public API as the old ChromaDB version.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_TOP_K
from rag.ingest_policies import _policy_text


def _chunk(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += size - overlap
    return chunks


def retrieve_policy_context(
    query: str,
    policy_type: str,
    top_k: int = RETRIEVAL_TOP_K,
) -> list[dict]:
    """
    Return text chunks for the given policy_type.
    Returns all chunks (not limited to top_k) so the validator has full policy context.
    Falls back to any available policy if the requested type is missing.
    """
    text = _policy_text.get(policy_type, "")
    if not text and _policy_text:
        text = next(iter(_policy_text.values()))
    if not text:
        return []

    return [
        {
            "content": chunk,
            "source_file": f"{policy_type}_policy.pdf",
            "policy_type": policy_type,
            "score": 1.0,
        }
        for chunk in _chunk(text)
    ]
