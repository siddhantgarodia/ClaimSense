import { useState } from 'react'
import { fetchSampleClaimFile } from '../api.js'

const CASES = [
  {
    id: 'claim_motor_valid',
    filename: 'claim_motor_valid.pdf',
    icon: '🚗',
    title: 'Valid Motor Claim',
    claimant: 'Rajesh Kumar',
    amount: 'INR 45,000',
    type: 'Motor',
    description: 'Collision damage claim with policy number POL-MOT-12345. Incident reported within the coverage period. Amount is within policy limits with no known exclusions.',
    expected: 'auto_approve',
    expectedLabel: 'Auto Approved',
    expectedColor: 'green',
    signals: ['Valid policy number', 'Amount within coverage', 'Timely filing', 'No exclusions'],
  },
  {
    id: 'claim_health_valid',
    filename: 'claim_health_valid.pdf',
    icon: '🏥',
    title: 'Valid Health Claim',
    claimant: 'Priya Sharma',
    amount: 'INR 80,000',
    type: 'Health',
    description: 'Hospitalisation claim for surgery under policy POL-HLT-67890. Coverage confirmed under the health policy. May require review if amount approaches policy limit.',
    expected: 'human_review',
    expectedLabel: 'Auto Approve or Review',
    expectedColor: 'yellow',
    signals: ['Valid health policy', 'Covered procedure', 'Amount near limit', 'Clean history'],
  },
  {
    id: 'claim_suspicious',
    filename: 'claim_suspicious.pdf',
    icon: '🚨',
    title: 'Suspicious Motor Claim',
    claimant: 'Anonymous',
    amount: 'INR 5,00,000',
    type: 'Motor',
    description: 'High-value motor claim filed 120 days after the incident with a vague description and a round amount (5 lakh INR). Multiple fraud rules are expected to trigger.',
    expected: 'reject',
    expectedLabel: 'Reject or Human Review',
    expectedColor: 'red',
    signals: ['90+ day delay', 'Round amount ≥ 50K', 'Vague description', 'Exceeds coverage'],
  },
]

const COLOR = {
  green:  { badge: 'bg-green-100 dark:bg-green-950/40 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800', ring: 'ring-green-400' },
  yellow: { badge: 'bg-yellow-100 dark:bg-yellow-950/40 text-yellow-700 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800', ring: 'ring-yellow-400' },
  red:    { badge: 'bg-red-100 dark:bg-red-950/40 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800', ring: 'ring-red-400' },
}

export default function TestCases({ onRunTest }) {
  const [loading, setLoading] = useState({})
  const [errors, setErrors] = useState({})

  async function handleRun(tc) {
    setLoading(prev => ({ ...prev, [tc.id]: true }))
    setErrors(prev => ({ ...prev, [tc.id]: null }))
    try {
      const file = await fetchSampleClaimFile(tc.filename)
      onRunTest(file)
    } catch (e) {
      setErrors(prev => ({ ...prev, [tc.id]: e.message }))
    } finally {
      setLoading(prev => ({ ...prev, [tc.id]: false }))
    }
  }

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Test Cases</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Pre-built sample claims to explore the full pipeline. Click <strong>Run Test</strong> to submit a sample and view the results.
        </p>
      </div>

      <div className="flex flex-col gap-4">
        {CASES.map(tc => {
          const c = COLOR[tc.expectedColor]
          const isLoading = loading[tc.id]
          const err = errors[tc.id]

          return (
            <div key={tc.id} className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl p-5 flex flex-col gap-4">
              {/* Header */}
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl bg-slate-50 dark:bg-slate-700 flex items-center justify-center text-2xl">
                    {tc.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{tc.title}</h3>
                    <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{tc.claimant} · {tc.amount} · {tc.type}</p>
                  </div>
                </div>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${c.badge}`}>
                  Expected: {tc.expectedLabel}
                </span>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{tc.description}</p>

              {/* Signals */}
              <div>
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5">Key signals:</p>
                <div className="flex flex-wrap gap-1.5">
                  {tc.signals.map(s => (
                    <span key={s} className="text-xs bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Error */}
              {err && (
                <p className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg px-3 py-2">
                  {err}
                </p>
              )}

              {/* Action */}
              <button
                onClick={() => handleRun(tc)}
                disabled={isLoading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Loading sample...
                  </>
                ) : (
                  <>▶ Run Test</>
                )}
              </button>
            </div>
          )
        })}
      </div>

      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700 px-4 py-3">
        <p className="text-xs text-slate-500 dark:text-slate-400">
          <strong className="text-slate-600 dark:text-slate-300">Note:</strong> Sample PDFs are served from the backend at <code className="font-mono text-xs">/api/samples/</code>.
          Running a test navigates to the Process Claim tab and starts the full pipeline. Results appear in the dashboard below the pipeline stepper.
        </p>
      </div>
    </div>
  )
}
