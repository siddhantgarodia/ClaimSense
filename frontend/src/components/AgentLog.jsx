export default function AgentLog({ log, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col border border-slate-100 dark:border-slate-700">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-700">
          <div className="flex items-center gap-2">
            <span className="text-lg">📋</span>
            <h3 className="font-semibold text-slate-800 dark:text-slate-100">Agent Processing Log</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl px-2 transition-colors">✕</button>
        </div>

        <div className="overflow-y-auto p-4 flex-1 font-mono text-xs space-y-1.5 bg-slate-50 dark:bg-slate-950/50">
          {log?.length > 0 ? log.map((entry, i) => (
            <div key={i} className="flex gap-3">
              <span className="text-slate-300 dark:text-slate-600 select-none w-6 text-right flex-shrink-0">
                {String(i + 1).padStart(2, '0')}
              </span>
              <span className={
                entry.toLowerCase().includes('failed') || entry.toLowerCase().includes('error')
                  ? 'text-red-500 dark:text-red-400'
                  : entry.toLowerCase().includes('complete') || entry.toLowerCase().includes('decision')
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-slate-600 dark:text-slate-300'
              }>{entry}</span>
            </div>
          )) : (
            <p className="text-slate-400 dark:text-slate-500">No log entries.</p>
          )}
        </div>

        <div className="px-5 py-4 border-t border-slate-100 dark:border-slate-700 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium transition-colors">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
