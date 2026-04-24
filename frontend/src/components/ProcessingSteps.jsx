const STEPS = [
  { key: 'extract',  label: 'Extract',     icon: '🔍', desc: 'Parsing claim document' },
  { key: 'validate', label: 'Validate',    icon: '📋', desc: 'Checking policy coverage via RAG' },
  { key: 'fraud',    label: 'Fraud Check', icon: '🛡️', desc: 'Rules + LLM anomaly detection' },
  { key: 'estimate', label: 'Estimate',    icon: '💰', desc: 'Calculating payout range' },
  { key: 'route',    label: 'Route',       icon: '🚦', desc: 'Final decision' },
]

function Badge({ status }) {
  if (status === 'done')    return <span className="text-green-500 font-bold">✓</span>
  if (status === 'active')  return <span className="inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
  return null
}

export default function ProcessingSteps({ currentStep }) {
  function getStatus(i) {
    if (currentStep === 5 || i < currentStep) return 'done'
    if (i === currentStep) return 'active'
    return 'pending'
  }

  return (
    <div className="w-full bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6">
      <h2 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-6">
        Agent Pipeline
      </h2>
      <div className="flex flex-col">
        {STEPS.map((step, i) => {
          const status = getStatus(i)
          return (
            <div key={step.key} className="flex items-start gap-4">
              <div className="flex flex-col items-center">
                <div className={[
                  'w-10 h-10 rounded-full flex items-center justify-center text-lg border-2 transition-all duration-500',
                  status === 'done'    ? 'bg-green-50 dark:bg-green-950/40 border-green-400' : '',
                  status === 'active'  ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-400 shadow-lg shadow-blue-100 dark:shadow-blue-900' : '',
                  status === 'pending' ? 'bg-slate-50 dark:bg-slate-700 border-slate-200 dark:border-slate-600' : '',
                ].join(' ')}>
                  {status === 'done' ? '✅' : step.icon}
                </div>
                {i < STEPS.length - 1 && (
                  <div className={`w-0.5 h-8 mt-1 transition-colors duration-500 ${status === 'done' ? 'bg-green-300 dark:bg-green-700' : 'bg-slate-200 dark:bg-slate-600'}`} />
                )}
              </div>
              <div className="flex-1 pt-2 pb-6">
                <div className="flex items-center gap-2">
                  <span className={`font-semibold text-sm ${
                    status === 'active'  ? 'text-blue-600 dark:text-blue-400' :
                    status === 'done'    ? 'text-green-700 dark:text-green-400' :
                    'text-slate-400 dark:text-slate-500'
                  }`}>{step.label}</span>
                  <Badge status={status} />
                </div>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{step.desc}</p>
              </div>
            </div>
          )
        })}
      </div>
      <p className="text-xs text-slate-400 dark:text-slate-500 text-center mt-1">
        {currentStep < 5 ? `Step ${currentStep + 1} of ${STEPS.length}` : 'All agents complete ✓'}
      </p>
    </div>
  )
}
