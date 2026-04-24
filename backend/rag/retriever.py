"""
Retrieves relevant policy chunks from ChromaDB, filtered by policy_type metadata.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import (
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    RETRIEVAL_TOP_K,
)

_embeddings = None
_vectorstore = None


def _get_vectorstore() -> Chroma:
    global _embeddings, _vectorstore
    if _vectorstore is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        _vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=_embeddings,
            persist_directory=CHROMA_DB_PATH,
        )
    return _vectorstore


def retrieve_policy_context(
    query: str,
    policy_type: str,
    top_k: int = RETRIEVAL_TOP_K,
) -> list[dict]:
    """
    Returns top_k policy chunks relevant to query, filtered by policy_type.
    Each result: {"content": str, "source_file": str, "policy_type": str, "score": float}
    """
    vs = _get_vectorstore()

    try:
        results = vs.similarity_search_with_relevance_scores(
            query,
            k=top_k,
            filter={"policy_type": policy_type},
        )
    except Exception:
        # Fallback without filter if metadata filter fails
        results = vs.similarity_search_with_relevance_scores(query, k=top_k)

    return [
        {
            "content": doc.page_content,
            "source_file": doc.metadata.get("source_file", "unknown"),
            "policy_type": doc.metadata.get("policy_type", policy_type),
            "score": float(score),
        }
        for doc, score in results
    ]
