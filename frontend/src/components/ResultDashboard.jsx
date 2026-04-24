import { useState } from 'react'
import AgentLog from './AgentLog.jsx'

function Card({ title, icon, children }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 p-5">
      <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-4 flex items-center gap-2">
        <span>{icon}</span> {title}
      </h3>
      {children}
    </div>
  )
}

function KV({ label, value }) {
  return (
    <div className="flex justify-between items-start gap-2 py-1.5 border-b border-slate-50 dark:border-slate-700 last:border-0">
      <span className="text-xs text-slate-500 dark:text-slate-400 flex-shrink-0 w-32">{label}</span>
      <span className="text-xs font-medium text-slate-800 dark:text-slate-200 text-right break-all">{value ?? '—'}</span>
    </div>
  )
}

function FraudGauge({ score }) {
  const pct = Math.round(score * 100)
  const color = pct < 30 ? '#22c55e' : pct < 70 ? '#eab308' : '#ef4444'
  const radius = 36
  const circ = 2 * Math.PI * radius
  const offset = circ - (pct / 100) * circ

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="96" height="96" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10" className="dark:stroke-slate-600" />
        <circle
          cx="48" cy="48" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 48 48)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text x="48" y="53" textAnchor="middle" fontSize="18" fontWeight="700" fill={color}>
          {pct}
        </text>
      </svg>
      <span className="text-xs font-semibold" style={{ color }}>
        {pct < 30 ? 'Low Risk' : pct < 70 ? 'Medium Risk' : 'High Risk'}
      </span>
    </div>
  )
}

function RangeBar({ min, estimated, max }) {
  if (!max || max === 0) return null
  const leftPct = ((min / max) * 100).toFixed(1)
  const estimatedPct = ((estimated / max) * 100).toFixed(1)

  return (
    <div className="mt-3">
      <div className="relative h-2 bg-slate-100 dark:bg-slate-700 rounded-full">
        <div
          className="absolute h-2 bg-blue-200 dark:bg-blue-900 rounded-full"
          style={{ left: `${leftPct}%`, right: '0%' }}
        />
        <div
          className="absolute w-3 h-3 bg-blue-600 rounded-full -top-0.5 shadow"
          style={{ left: `calc(${estimatedPct}% - 6px)` }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-400 dark:text-slate-500 mt-1">
        <span>INR {(min || 0).toLocaleString()}</span>
        <span>INR {(max || 0).toLocaleString()}</span>
      </div>
    </div>
  )
}

const DECISION_STYLES = {
  auto_approve: {
    bg: 'bg-green-50 dark:bg-green-950/40',
    border: 'border-green-300 dark:border-green-700',
    text: 'text-green-800 dark:text-green-300',
    badge: 'bg-green-600 text-white',
    icon: '✅',
    label: 'Auto Approved',
  },
  human_review: {
    bg: 'bg-yellow-50 dark:bg-yellow-950/40',
    border: 'border-yellow-300 dark:border-yellow-700',
    text: 'text-yellow-900 dark:text-yellow-300',
    badge: 'bg-yellow-500 text-white',
    icon: '👤',
    label: 'Human Review Required',
  },
  reject: {
    bg: 'bg-red-50 dark:bg-red-950/40',
    border: 'border-red-300 dark:border-red-700',
    text: 'text-red-900 dark:text-red-300',
    badge: 'bg-red-600 text-white',
    icon: '❌',
    label: 'Rejected',
  },
}

export default function ResultDashboard({ result, onReset }) {
  const [showLog, setShowLog] = useState(false)
  const { extraction: ex, policy_validation: pv, fraud_assessment: fa, payout_estimate: pe, routing_decision: rd } = result
  const ds = DECISION_STYLES[rd?.decision] || DECISION_STYLES.human_review

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Routing Decision Banner */}
      <div className={`rounded-xl border-2 ${ds.bg} ${ds.border} p-5`}>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{ds.icon}</span>
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${ds.badge}`}>
                  {ds.label}
                </span>
                <span className={`text-xs ${ds.text}`}>
                  {Math.round((rd?.confidence || 0) * 100)}% confidence
                </span>
              </div>
              <p className={`text-sm mt-1 ${ds.text}`}>{rd?.reasoning}</p>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setShowLog(true)}
              className="px-3 py-1.5 text-xs font-medium bg-white/70 dark:bg-slate-700/70 hover:bg-white dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-300 transition-colors"
            >
              View Agent Log
            </button>
            <button
              onClick={onReset}
              className="px-3 py-1.5 text-xs font-medium bg-white/70 dark:bg-slate-700/70 hover:bg-white dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-300 transition-colors"
            >
              New Claim
            </button>
          </div>
        </div>
      </div>

      {/* 2x2 Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

        {/* Card 1: Extracted Data */}
        <Card title="Extracted Data" icon="🔍">
          {ex ? (
            <div>
              <KV label="Claimant" value={ex.claimant_name} />
              <KV label="Policy #" value={ex.policy_number} />
              <KV label="Type" value={ex.claim_type?.toUpperCase()} />
              <KV label="Incident Date" value={ex.incident_date} />
              <KV label="Amount" value={`INR ${(ex.claim_amount || 0).toLocaleString()}`} />
              <KV label="Confidence" value={`${Math.round((ex.extraction_confidence || 0) * 100)}%`} />
              <div className="mt-2">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Description</p>
                <p className="text-xs text-slate-700 dark:text-slate-300 line-clamp-3">{ex.incident_description}</p>
              </div>
              {ex.damage_items?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {ex.damage_items.map((item, i) => (
                    <span key={i} className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full">
                      {item}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-400 dark:text-slate-500">Extraction data unavailable.</p>
          )}
        </Card>

        {/* Card 2: Policy Validation */}
        <Card title="Policy Match" icon="📋">
          {pv ? (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">
                  {pv.coverage_applies ? '✅' : pv.policy_found ? '⚠️' : '❌'}
                </span>
                <span className={`text-sm font-semibold ${pv.coverage_applies ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}`}>
                  {pv.coverage_applies ? 'Coverage Applies' : pv.policy_found ? 'Partial Coverage' : 'Not Covered'}
                </span>
              </div>
              <KV label="Policy Found" value={pv.policy_found ? 'Yes' : 'No'} />
              <KV label="Policy Active" value={pv.policy_active ? 'Yes' : 'No'} />
              <KV label="Max Coverage" value={pv.max_coverage_amount ? `INR ${pv.max_coverage_amount.toLocaleString()}` : 'Unknown'} />
              <KV label="Confidence" value={`${Math.round((pv.validation_confidence || 0) * 100)}%`} />
              {pv.exclusions_triggered?.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-red-500 dark:text-red-400 font-medium mb-1">Exclusions Triggered</p>
                  <ul className="text-xs text-red-700 dark:text-red-400 space-y-0.5">
                    {pv.exclusions_triggered.map((e, i) => <li key={i}>• {e}</li>)}
                  </ul>
                </div>
              )}
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 italic">{pv.validation_notes}</p>
            </div>
          ) : (
            <p className="text-xs text-slate-400 dark:text-slate-500">Policy validation skipped.</p>
          )}
        </Card>

        {/* Card 3: Fraud Risk */}
        <Card title="Fraud Risk" icon="🛡️">
          {fa ? (
            <div>
              <FraudGauge score={fa.risk_score} />
              {fa.rule_flags?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Rule Flags</p>
                  <ul className="text-xs text-orange-700 dark:text-orange-400 space-y-0.5">
                    {fa.rule_flags.map((f, i) => <li key={i}>• {f}</li>)}
                  </ul>
                </div>
              )}
              {fa.llm_concerns?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">LLM Concerns</p>
                  <ul className="text-xs text-red-700 dark:text-red-400 space-y-0.5">
                    {fa.llm_concerns.map((c, i) => <li key={i}>• {c}</li>)}
                  </ul>
                </div>
              )}
              {(!fa.rule_flags?.length && !fa.llm_concerns?.length) && (
                <p className="text-xs text-green-600 dark:text-green-400 mt-2">No fraud signals detected.</p>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-400 dark:text-slate-500">Fraud assessment skipped.</p>
          )}
        </Card>

        {/* Card 4: Payout Estimate */}
        <Card title="Payout Estimate" icon="💰">
          {pe ? (
            <div>
              <div className="text-3xl font-bold text-slate-800 dark:text-slate-100 mb-1">
                INR {(pe.estimated_amount || 0).toLocaleString()}
              </div>
              <RangeBar min={pe.min_amount} estimated={pe.estimated_amount} max={pe.max_amount} />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-3 italic leading-relaxed">{pe.reasoning}</p>
            </div>
          ) : (
            <p className="text-xs text-slate-400 dark:text-slate-500">Payout estimate skipped (high fraud risk or coverage not applicable).</p>
          )}
        </Card>
      </div>

      {result.error && (
        <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg p-3 text-xs text-red-700 dark:text-red-400">
          <strong>Processing note:</strong> {result.error}
        </div>
      )}

      {showLog && (
        <AgentLog log={result.processing_log} onClose={() => setShowLog(false)} />
      )}
    </div>
  )
}
