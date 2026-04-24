const PIPELINE = [
  {
    step: 1,
    icon: '🔍',
    name: 'Extract',
    model: 'LLM (Groq)',
    desc: 'The claim PDF is parsed and passed to Llama 3.3 70B with structured output prompting. The model extracts claimant name, policy number, incident date, claim amount, type, and damage items into a typed Pydantic schema.',
    output: 'ClaimExtraction',
    color: 'blue',
  },
  {
    step: 2,
    icon: '📋',
    name: 'Validate',
    model: 'RAG + LLM',
    desc: 'The claim type is used to filter ChromaDB for matching policy chunks. The top-4 most semantically similar policy excerpts are injected into a prompt that asks the LLM to determine coverage applicability, policy status, maximum coverage, and any triggered exclusions.',
    output: 'PolicyValidation',
    color: 'purple',
  },
  {
    step: 3,
    icon: '🛡️',
    name: 'Fraud Check',
    model: 'Rules + LLM',
    desc: 'A hybrid detector runs first: 5 deterministic rules flag issues like amounts exceeding coverage, future incident dates, 90-day delays, triggered exclusions, and suspiciously round numbers. The LLM then provides a semantic risk score. Final score = 60% rules + 40% LLM.',
    output: 'FraudAssessment',
    color: 'orange',
  },
  {
    step: 4,
    icon: '💰',
    name: 'Estimate',
    model: 'LLM (Groq)',
    desc: 'Given the validated claim and policy context, the LLM calculates a realistic payout range (min / estimated / max) and provides reasoning. This step is skipped if fraud risk is ≥0.8 or coverage does not apply.',
    output: 'PayoutEstimate',
    color: 'green',
  },
  {
    step: 5,
    icon: '🚦',
    name: 'Route',
    model: 'Pure Logic',
    desc: 'A deterministic decision tree makes the final call: extraction confidence <50% → human review; fraud ≥80% → reject; no coverage → reject; fraud ≥30% → human review; everything clean → auto-approve. No LLM call — fully auditable.',
    output: 'RoutingDecision',
    color: 'slate',
  },
]

const TECH = [
  { icon: '🧠', name: 'Llama 3.3 70B', via: 'via Groq API', desc: 'Extraction, validation, fraud scoring, payout estimation' },
  { icon: '🔗', name: 'LangGraph', via: 'StateGraph', desc: 'Orchestrates the 5-agent pipeline with conditional edges and shared state' },
  { icon: '📦', name: 'ChromaDB', via: 'Persistent store', desc: 'Stores policy document chunks with metadata for filtered retrieval' },
  { icon: '🤗', name: 'all-MiniLM-L6-v2', via: 'HuggingFace', desc: 'Generates sentence embeddings for semantic similarity search' },
  { icon: '⚡', name: 'FastAPI', via: 'Python backend', desc: 'Async HTTP server with thread executor for sync LangGraph pipeline' },
  { icon: '⚛️', name: 'React + Vite', via: 'Frontend', desc: 'Single-page app with Tailwind CSS and dark mode support' },
]

const COLOR_MAP = {
  blue:   { dot: 'bg-blue-500',   badge: 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800' },
  purple: { dot: 'bg-purple-500', badge: 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800' },
  orange: { dot: 'bg-orange-500', badge: 'bg-orange-50 dark:bg-orange-950/40 text-orange-700 dark:text-orange-300 border-orange-200 dark:border-orange-800' },
  green:  { dot: 'bg-green-500',  badge: 'bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800' },
  slate:  { dot: 'bg-slate-400',  badge: 'bg-slate-50 dark:bg-slate-700 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-600' },
}

export default function HowItWorks() {
  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-10">
      {/* Intro */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">How ClaimSense Works</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
          ClaimSense is an AI-native insurance claim processor built on a multi-agent LangGraph pipeline.
          Each uploaded PDF flows through five specialised agents, combining LLM reasoning, retrieval-augmented generation,
          and deterministic rules to reach an auditable decision in under 60 seconds.
        </p>
      </div>

      {/* Architecture diagram (text-based) */}
      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700 p-6">
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-5">Pipeline Overview</h3>
        <div className="flex items-center gap-1 flex-wrap">
          {['PDF Upload', 'Extract', 'Validate', 'Fraud Check', 'Estimate', 'Route', 'Decision'].map((label, i, arr) => (
            <div key={label} className="flex items-center gap-1">
              <span className={`text-xs font-medium px-2.5 py-1 rounded-lg whitespace-nowrap ${
                i === 0 || i === arr.length - 1
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                  : 'bg-blue-600 text-white'
              }`}>{label}</span>
              {i < arr.length - 1 && (
                <span className="text-slate-300 dark:text-slate-600 font-mono">→</span>
              )}
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-3">
          Conditional edges skip Estimate if fraud is critical. LangGraph's StateGraph manages shared state between agents.
        </p>
      </div>

      {/* Agent pipeline detail */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4">The 5 Agents</h3>
        <div className="flex flex-col">
          {PIPELINE.map((agent, i) => {
            const c = COLOR_MAP[agent.color]
            return (
              <div key={agent.step} className="flex gap-4 relative">
                {/* Timeline */}
                <div className="flex flex-col items-center flex-shrink-0" style={{ width: 32 }}>
                  <div className={`w-8 h-8 rounded-full ${c.dot} flex items-center justify-center text-white font-bold text-sm`}>
                    {agent.step}
                  </div>
                  {i < PIPELINE.length - 1 && (
                    <div className="w-0.5 bg-slate-200 dark:bg-slate-700 flex-1 my-1 min-h-8" />
                  )}
                </div>

                {/* Content */}
                <div className={`flex-1 pb-8 ${i === PIPELINE.length - 1 ? 'pb-0' : ''}`}>
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-lg">{agent.icon}</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{agent.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${c.badge}`}>{agent.model}</span>
                    <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">→ {agent.output}</span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{agent.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* RAG explanation */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6">
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">RAG — Retrieval-Augmented Generation</h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-3">
          Policy documents are split into 500-character overlapping chunks and embedded with
          <code className="mx-1 font-mono text-xs bg-slate-100 dark:bg-slate-700 px-1 py-0.5 rounded">all-MiniLM-L6-v2</code>
          into ChromaDB. Each chunk is tagged with its policy type (motor, health, home, life).
        </p>
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          At validation time, the claim type is used to metadata-filter the collection, then the top-4
          semantically nearest chunks are retrieved and injected directly into the validation prompt —
          giving the LLM grounded context about what the policy actually covers, without hallucination.
        </p>
      </div>

      {/* Fraud detection */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6">
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">Hybrid Fraud Detection</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">Deterministic Rules (60% weight)</p>
            <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
              {[
                'Amount exceeds maximum policy coverage',
                'Incident date is in the future',
                'Claim filed more than 90 days after incident',
                'A policy exclusion has been triggered',
                'Round amount ≥ INR 50,000 (e.g. 100000)',
              ].map((r, i) => <li key={i}>• {r}</li>)}
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">LLM Semantic Analysis (40% weight)</p>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              The LLM receives the full claim context and policy validation and returns a risk score with
              natural-language concerns — detecting vague descriptions, inconsistencies, and patterns
              that rules alone would miss.
            </p>
          </div>
        </div>
        <div className="mt-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg px-3 py-2">
          <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">
            final_score = 0.6 × rule_score + 0.4 × llm_score
            <span className="ml-3 text-slate-400">|</span>
            <span className="ml-3">{'<'}0.3 → proceed, {'<'}0.7 → review, ≥0.7 → investigate</span>
          </p>
        </div>
      </div>

      {/* Tech stack */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4">Technology Stack</h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {TECH.map(t => (
            <div key={t.name} className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-xl p-4 flex gap-3">
              <span className="text-2xl flex-shrink-0">{t.icon}</span>
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{t.name}</p>
                <p className="text-xs text-slate-400 dark:text-slate-500">{t.via}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{t.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Design decisions */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6">
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">Design Decisions</h3>
        <dl className="flex flex-col gap-3">
          {[
            ['Why Groq instead of OpenAI/Gemini?', 'Groq\'s inference API offers the fastest LLM response times, critical for keeping the end-to-end pipeline under 60 seconds.'],
            ['Why LangGraph instead of a simple chain?', 'LangGraph\'s StateGraph provides conditional routing (skipping Estimate on high fraud), shared typed state, and a visible execution log — all essential for an auditable insurance workflow.'],
            ['Why hybrid fraud detection?', 'Rules catch objective violations (future dates, round numbers) with zero hallucination risk. The LLM catches subjective patterns (vague language, inconsistency) that rules miss. The weighted combination is more robust than either alone.'],
            ['Why PDF text truncation?', 'LLM token-per-minute limits on free-tier APIs. The first 3 pages (~4000 chars) contain all claim fields; truncation prevents rate-limit errors without losing material information.'],
            ['Why a deterministic router?', 'The final decision is pure logic — no LLM call. This makes it auditable, reproducible, and explainable to regulators. The LLM informs the inputs; the rule decides the output.'],
          ].map(([q, a]) => (
            <div key={q} className="border-b border-slate-100 dark:border-slate-700 pb-3 last:border-0 last:pb-0">
              <dt className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">{q}</dt>
              <dd className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{a}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  )
}
