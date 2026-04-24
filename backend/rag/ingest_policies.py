"""
Ingests policy PDFs into ChromaDB. Run once before starting the server,
or called automatically on startup via main.py. Idempotent — skips if
collection already has data unless force_reingest=True.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import (
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    POLICY_DOCS_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def _get_vectorstore(embeddings: HuggingFaceEmbeddings) -> Chroma:
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )


def ingest_all_policies(force_reingest: bool = False) -> dict:
    """
    Reads all policy PDFs in POLICY_DOCS_PATH, chunks them, embeds, and stores in ChromaDB.
    Returns a dict mapping policy_type -> number of chunks ingested.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = _get_vectorstore(embeddings)

    # Check if already ingested
    if not force_reingest:
        try:
            existing = vectorstore._collection.count()
            if existing > 0:
                print(f"[RAG] Collection already has {existing} chunks. Skipping ingestion (use force_reingest=True to re-run).")
                return {}
        except Exception:
            pass

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    policy_dir = Path(POLICY_DOCS_PATH)
    if not policy_dir.exists():
        raise FileNotFoundError(f"Policy directory not found: {policy_dir}")

    results = {}

    for pdf_path in sorted(policy_dir.glob("*.pdf")):
        # Infer policy type from filename: "motor_policy.pdf" -> "motor"
        policy_type = pdf_path.stem.replace("_policy", "")

        reader = PdfReader(str(pdf_path))
        full_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()

        if not full_text:
            print(f"[RAG] WARNING: No text extracted from {pdf_path.name}")
            continue

        chunks = splitter.split_text(full_text)
        docs = []
        metadatas = []

        for chunk in chunks:
            docs.append(chunk)
            metadatas.append({
                "policy_type": policy_type,
                "source_file": pdf_path.name,
            })

        vectorstore.add_texts(texts=docs, metadatas=metadatas)
        results[policy_type] = len(chunks)
        print(f"[RAG] Ingested {pdf_path.name}: {len(chunks)} chunks (type={policy_type})")

    return results


def ingest_single_policy(pdf_path: Path, policy_type: str) -> int:
    """
    Ingest (or re-ingest) a single policy PDF into ChromaDB.
    Deletes existing chunks for this policy_type first, then adds the new ones.
    Returns the number of chunks ingested.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )

    # Remove stale chunks for this policy type
    try:
        vectorstore._collection.delete(where={"policy_type": policy_type})
        print(f"[RAG] Cleared old chunks for policy_type={policy_type}")
    except Exception as e:
        print(f"[RAG] Warning: could not clear old chunks: {e}")

    reader = PdfReader(str(pdf_path))
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not full_text:
        raise ValueError(f"No text extracted from {pdf_path.name}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_text(full_text)
    metadatas = [{"policy_type": policy_type, "source_file": pdf_path.name} for _ in chunks]
    vectorstore.add_texts(texts=chunks, metadatas=metadatas)
    print(f"[RAG] Ingested {len(chunks)} chunks for policy_type={policy_type} from {pdf_path.name}")
    return len(chunks)


if __name__ == "__main__":
    result = ingest_all_policies(force_reingest=True)
    print(f"\nIngestion complete: {result}")
