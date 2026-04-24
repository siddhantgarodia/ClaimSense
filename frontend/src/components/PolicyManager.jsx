import { useState, useEffect, useRef } from 'react'
import { fetchPolicies, uploadPolicy } from '../api.js'

const POLICY_TYPES = [
  { value: 'motor',  label: 'Motor',  icon: '🚗' },
  { value: 'health', label: 'Health', icon: '🏥' },
  { value: 'home',   label: 'Home',   icon: '🏠' },
  { value: 'life',   label: 'Life',   icon: '❤️' },
]

const TYPE_ICONS = { motor: '🚗', health: '🏥', home: '🏠', life: '❤️', other: '📄' }

function PolicyCard({ policy, onReplace }) {
  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-xl p-4 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-950/40 flex items-center justify-center text-xl">
          {TYPE_ICONS[policy.type] || '📄'}
        </div>
        <div>
          <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm capitalize">
            {policy.type} Policy
          </p>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
            {policy.chunks} chunks · {policy.source_file}
          </p>
        </div>
      </div>
      <button
        onClick={() => onReplace(policy.type)}
        className="text-xs px-3 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-500 dark:text-slate-400 hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
      >
        Replace
      </button>
    </div>
  )
}

export default function PolicyManager() {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [selectedType, setSelectedType] = useState('motor')
  const [replaceTarget, setReplaceTarget] = useState(null)
  const fileRef = useRef(null)

  async function loadPolicies() {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchPolicies()
      setPolicies(data.policies ?? data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadPolicies() }, [])

  async function handleUpload(file) {
    if (!file) return
    const type = replaceTarget || selectedType
    setUploading(true)
    setUploadResult(null)
    try {
      const res = await uploadPolicy(file, type)
      setUploadResult({ ok: true, message: `${res.message} (${res.chunks_added} chunks ingested)` })
      setReplaceTarget(null)
      await loadPolicies()
    } catch (e) {
      setUploadResult({ ok: false, message: e.message })
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const existingTypes = new Set(policies.map(p => p.type))

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Policy Library</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Manage the policy documents used for RAG-based coverage validation.
        </p>
      </div>

      {/* Current policies */}
      <div className="flex flex-col gap-3">
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          Ingested Policies
        </h3>
        {loading ? (
          <div className="text-sm text-slate-400 dark:text-slate-500 py-4 text-center">Loading...</div>
        ) : error ? (
          <div className="text-sm text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3">
            {error}
          </div>
        ) : policies.length === 0 ? (
          <div className="text-sm text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-slate-800/50 rounded-xl px-4 py-6 text-center border border-dashed border-slate-200 dark:border-slate-700">
            No policies ingested yet. Upload a policy PDF below to get started.
          </div>
        ) : (
          policies.map(p => (
            <PolicyCard key={p.type} policy={p} onReplace={type => { setReplaceTarget(type); fileRef.current?.click() }} />
          ))
        )}
      </div>

      {/* Upload new policy */}
      <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-xl p-5">
        <h3 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4">
          Upload New Policy
        </h3>

        <div className="flex flex-col gap-3">
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1.5 block">Policy Type</label>
            <div className="flex flex-wrap gap-2">
              {POLICY_TYPES.map(pt => (
                <button
                  key={pt.value}
                  onClick={() => setSelectedType(pt.value)}
                  disabled={uploading}
                  className={[
                    'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border transition-all',
                    selectedType === pt.value
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-blue-400',
                    existingTypes.has(pt.value) ? 'ring-1 ring-offset-1 ring-amber-400 dark:ring-offset-slate-800' : '',
                  ].join(' ')}
                >
                  <span>{pt.icon}</span> {pt.label}
                  {existingTypes.has(pt.value) && <span className="text-xs opacity-70">(replace)</span>}
                </button>
              ))}
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1.5">
              {existingTypes.has(selectedType) ? 'Uploading will replace the existing policy and re-ingest chunks.' : 'No policy of this type is currently loaded.'}
            </p>
          </div>

          <div>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={e => { handleUpload(e.target.files[0]); e.target.value = '' }}
              disabled={uploading}
            />
            <button
              onClick={() => { setReplaceTarget(null); fileRef.current?.click() }}
              disabled={uploading}
              className="w-full py-2.5 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 text-sm text-slate-500 dark:text-slate-400 hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <>
                  <span className="inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                  Ingesting policy into ChromaDB...
                </>
              ) : (
                <>📂 Choose PDF to upload</>
              )}
            </button>
          </div>

          {uploadResult && (
            <div className={`text-xs px-4 py-3 rounded-lg border flex items-start gap-2 ${
              uploadResult.ok
                ? 'bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400'
                : 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400'
            }`}>
              <span>{uploadResult.ok ? '✅' : '⚠️'}</span>
              <span>{uploadResult.message}</span>
            </div>
          )}
        </div>
      </div>

      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700 px-4 py-3">
        <p className="text-xs text-slate-500 dark:text-slate-400">
          <strong className="text-slate-600 dark:text-slate-300">How it works:</strong> Uploaded PDFs are split into 500-character chunks,
          embedded using <code className="font-mono">all-MiniLM-L6-v2</code>, and stored in ChromaDB with metadata filtering.
          During claim validation, the top-4 most relevant chunks are retrieved by semantic similarity.
        </p>
      </div>
    </div>
  )
}
