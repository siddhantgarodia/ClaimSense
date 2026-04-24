# ClaimSense

**AI-native insurance claim processor with human-in-the-loop review**

Upload a claim PDF — ClaimSense runs it through a 5-agent LangGraph pipeline (Extract → Validate → Fraud → Estimate → Route) and returns a full decision dashboard with confidence scores and a step-by-step audit trail.

---

## Architecture

```
React + Vite + Tailwind (port 5173)
        │ HTTP/JSON
        ▼
FastAPI (port 8000)
        │
        ▼
  LangGraph Orchestrator
  ├─ [1] Extractor     — Gemini 2.0 Flash + Pydantic structured output
  ├─ [2] Policy Validator — RAG (ChromaDB + sentence-transformers)
  ├─ [3] Fraud Checker — Hardcoded rules + Gemini semantic analysis
  ├─ [4] Payout Estimator — Gemini 2.0 Flash
  └─ [5] Router        — Pure logic, confidence-gated
```

## Key Design Decisions

- **Pydantic structured outputs** — every LLM response is parsed into a typed model, eliminating a whole class of output parsing bugs
- **Metadata-filtered RAG** — policy chunks are filtered by `claim_type` at retrieval time, improving precision
- **Hybrid fraud detection** — hardcoded rules catch definite violations (future dates, round amounts, late filing); LLM catches semantic fraud (vague descriptions, implausible damage)
- **Confidence-gated routing** — low-confidence extractions skip downstream agents entirely and go straight to human review
- **Graceful degradation** — every agent catches exceptions and returns a valid default object; the pipeline never crashes

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 5, Tailwind CSS 3 |
| Backend | FastAPI, Uvicorn |
| Orchestration | LangGraph 0.2 |
| LLM | Gemini 2.0 Flash (free tier) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | ChromaDB (persistent) |
| PDF parsing | pypdf |
| Data validation | Pydantic v2 |

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Free Google AI Studio API key: https://aistudio.google.com

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add your Gemini API key
cp .env.example .env
# Edit .env and set: GOOGLE_API_KEY=your_key_here

# Generate sample PDFs (run once)
python scripts/generate_sample_pdfs.py

# Start the server
uvicorn main:app --reload
```

The server ingests policy documents into ChromaDB automatically on first startup.

> **First run note:** The embedding model (~80 MB) downloads on first use. This takes 1–2 minutes. Subsequent runs use the local cache.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

### 3. Test it

Drop one of these sample PDFs onto the upload zone:

| File | Expected outcome |
|---|---|
| `backend/data/sample_claims/claim_motor_valid.pdf` | Auto-approve (clean motor claim, INR 45,000) |
| `backend/data/sample_claims/claim_health_valid.pdf` | Auto-approve or human review (health surgery, INR 80,000) |
| `backend/data/sample_claims/claim_suspicious.pdf` | Reject (INR 500,000, 120 days late, vague description) |

---

## Project Structure

```
ClaimSense/
├── backend/
│   ├── main.py              # FastAPI app — HTTP endpoints
│   ├── graph.py             # LangGraph state machine
│   ├── config.py            # Central config + constants
│   ├── schemas/claim.py     # Pydantic models (data contracts)
│   ├── agents/
│   │   ├── extractor.py
│   │   ├── policy_validator.py
│   │   ├── fraud_checker.py
│   │   ├── estimator.py
│   │   └── router.py
│   ├── rag/
│   │   ├── ingest_policies.py
│   │   └── retriever.py
│   ├── prompts/             # LLM prompt templates
│   ├── data/
│   │   ├── sample_policies/ # 3 policy PDFs (ingested into ChromaDB)
│   │   └── sample_claims/   # 3 test claim PDFs
│   └── scripts/
│       └── generate_sample_pdfs.py
└── frontend/
    └── src/
        ├── App.jsx
        ├── api.js
        └── components/
            ├── UploadZone.jsx
            ├── ProcessingSteps.jsx
            ├── ResultDashboard.jsx
            └── AgentLog.jsx
```

---

## Future Improvements

- **RAGAS** integration for continuous retrieval quality evaluation
- **OCR** for scanned PDFs (Tesseract / Google Document AI)
- **pgvector** as a ChromaDB replacement at scale
- **Streaming** responses so the frontend shows live agent output
- **Fine-tuned embeddings** on claim-specific language
- **Webhook-based policy re-ingestion** when policies are updated

## License

MIT
