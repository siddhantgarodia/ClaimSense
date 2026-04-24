import { useState } from 'react'
import UploadZone from './components/UploadZone.jsx'
import ProcessingSteps from './components/ProcessingSteps.jsx'
import ResultDashboard from './components/ResultDashboard.jsx'
import PolicyManager from './components/PolicyManager.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import TestCases from './components/TestCases.jsx'
import { processClaim } from './api.js'

const STEP_DELAYS = [1200, 2400, 3600, 4800]

const NAV = [
  { id: 'process', label: 'Process Claim', icon: '📄' },
  { id: 'tests',   label: 'Test Cases',    icon: '🧪' },
  { id: 'policies',label: 'Policies',      icon: '📚' },
  { id: 'how',     label: 'How It Works',  icon: '💡' },
]

function useDarkMode() {
  const [dark, setDark] = useState(
    () => document.documentElement.classList.contains('dark')
  )

  function toggle() {
    const next = !dark
    document.documentElement.classList.toggle('dark', next)
    localStorage.setItem('claimsense-dark', String(next))
    setDark(next)
  }

  return [dark, toggle]
}

export default function App() {
  const [dark, toggleDark] = useDarkMode()
  const [activeTab, setActiveTab] = useState('process')
  const [claimState, setClaimState] = useState({
    status: 'idle',
    currentStep: 0,
    result: null,
    error: null,
  })

  async function handleFileSelect(file) {
    setActiveTab('process')
    setClaimState({ status: 'processing', currentStep: 0, result: null, error: null })

    const timers = STEP_DELAYS.map((delay, i) =>
      setTimeout(() => {
        setClaimState(prev =>
          prev.status === 'processing' ? { ...prev, currentStep: i + 1 } : prev
        )
      }, delay)
    )

    try {
      const result = await processClaim(file)
      timers.forEach(clearTimeout)
      setClaimState({ status: 'complete', currentStep: 5, result, error: null })
    } catch (err) {
      timers.forEach(clearTimeout)
      setClaimState({
        status: 'error',
        currentStep: 0,
        result: null,
        error: err.message || 'An unexpected error occurred.',
      })
    }
  }

  function handleReset() {
    setClaimState({ status: 'idle', currentStep: 0, result: null, error: null })
  }

  const isProcessing = claimState.status === 'processing'

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800 sticky top-0 z-40 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-14">
            {/* Logo */}
            <button
              onClick={() => setActiveTab('process')}
              className="flex items-center gap-2.5 flex-shrink-0"
            >
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm select-none">
                CS
              </div>
              <div className="leading-none">
                <p className="text-sm font-bold text-slate-900 dark:text-slate-100">ClaimSense</p>
                <p className="text-xs text-slate-400 dark:text-slate-500 hidden sm:block">AI claim processor</p>
              </div>
            </button>

            {/* Nav tabs — desktop */}
            <nav className="hidden md:flex items-center gap-1">
              {NAV.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={[
                    'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                    activeTab === tab.id
                      ? 'bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400'
                      : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800',
                  ].join(' ')}
                >
                  <span className="text-base">{tab.icon}</span>
                  {tab.label}
                  {tab.id === 'process' && isProcessing && (
                    <span className="ml-1 w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                  )}
                </button>
              ))}
            </nav>

            {/* Right controls */}
            <div className="flex items-center gap-2">
              {/* Status pill — desktop */}
              <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 px-2 py-1 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                Llama 3.3 · LangGraph · RAG
              </div>
              {/* Dark mode toggle */}
              <button
                onClick={toggleDark}
                className="w-9 h-9 flex items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors"
                aria-label="Toggle dark mode"
              >
                {dark ? '☀️' : '🌙'}
              </button>
            </div>
          </div>

          {/* Nav tabs — mobile */}
          <nav className="flex md:hidden items-center gap-0.5 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-none">
            {NAV.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={[
                  'flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap flex-shrink-0 transition-colors',
                  activeTab === tab.id
                    ? 'bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200',
                ].join(' ')}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">

        {/* ── Process Claim tab ── */}
        {activeTab === 'process' && (
          <>
            {claimState.status === 'idle' && (
              <div className="max-w-xl mx-auto">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                    Process an Insurance Claim
                  </h2>
                  <p className="text-slate-500 dark:text-slate-400 text-sm">
                    Upload a claim PDF. Five AI agents will extract, validate, assess fraud,
                    estimate payout, and route to an auditable decision.
                  </p>
                </div>
                <UploadZone onFileSelect={handleFileSelect} disabled={false} />
                <p className="text-center text-xs text-slate-400 dark:text-slate-500 mt-4">
                  Want to try a sample?{' '}
                  <button onClick={() => setActiveTab('tests')} className="text-blue-500 hover:underline">
                    Browse test cases →
                  </button>
                </p>
              </div>
            )}

            {claimState.status === 'processing' && (
              <div className="flex flex-col lg:flex-row gap-6">
                <div className="lg:w-72 flex-shrink-0">
                  <ProcessingSteps currentStep={claimState.currentStep} />
                </div>
                <div className="flex-1 flex items-center justify-center min-h-64">
                  <div className="text-center text-slate-400 dark:text-slate-500">
                    <div className="text-5xl mb-4 animate-pulse">⚙️</div>
                    <p className="font-medium text-slate-600 dark:text-slate-300">Agents are working...</p>
                    <p className="text-sm mt-1">This takes 20–60 seconds depending on the claim.</p>
                  </div>
                </div>
              </div>
            )}

            {claimState.status === 'complete' && claimState.result && (
              <div className="flex flex-col lg:flex-row gap-6">
                <div className="lg:w-72 flex-shrink-0">
                  <ProcessingSteps currentStep={5} />
                </div>
                <div className="flex-1">
                  <ResultDashboard result={claimState.result} onReset={handleReset} />
                </div>
              </div>
            )}

            {claimState.status === 'error' && (
              <div className="max-w-xl mx-auto">
                <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center mb-6">
                  <div className="text-4xl mb-3">❌</div>
                  <h3 className="text-lg font-semibold text-red-800 dark:text-red-300 mb-2">Processing Failed</h3>
                  <p className="text-sm text-red-700 dark:text-red-400">{claimState.error}</p>
                </div>
                <UploadZone onFileSelect={handleFileSelect} disabled={false} />
              </div>
            )}
          </>
        )}

        {/* ── Test Cases tab ── */}
        {activeTab === 'tests' && (
          <TestCases onRunTest={handleFileSelect} />
        )}

        {/* ── Policies tab ── */}
        {activeTab === 'policies' && (
          <PolicyManager />
        )}

        {/* ── How It Works tab ── */}
        {activeTab === 'how' && (
          <HowItWorks />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-100 dark:border-slate-800 py-6">
        <p className="text-center text-xs text-slate-400 dark:text-slate-500">
          ClaimSense · LangGraph · ChromaDB · Groq · FastAPI · React
        </p>
      </footer>
    </div>
  )
}
