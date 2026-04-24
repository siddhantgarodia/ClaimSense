import { useState, useRef } from 'react'

const MAX_SIZE = 10 * 1024 * 1024

export default function UploadZone({ onFileSelect, disabled }) {
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  function validate(file) {
    if (!file) return 'No file selected.'
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf')
      return 'Only PDF files are accepted.'
    if (file.size > MAX_SIZE)
      return `File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum is 10 MB.`
    return null
  }

  function handleFile(file) {
    const err = validate(file)
    if (err) { setError(err); return }
    setError(null)
    onFileSelect(file)
  }

  return (
    <div className="flex flex-col items-center gap-3 w-full">
      <div
        onDrop={e => { e.preventDefault(); setDragOver(false); if (!disabled) handleFile(e.dataTransfer.files[0]) }}
        onDragOver={e => { e.preventDefault(); if (!disabled) setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !disabled && inputRef.current?.click()}
        className={[
          'w-full border-2 border-dashed rounded-2xl p-12 flex flex-col items-center gap-4',
          'cursor-pointer transition-all duration-200 select-none',
          disabled
            ? 'opacity-50 cursor-not-allowed bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700'
            : dragOver
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40 scale-[1.01]'
              : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800/50 hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30',
        ].join(' ')}
      >
        <div className={`text-5xl transition-transform duration-200 ${dragOver ? 'scale-125' : ''}`}>
          {dragOver ? '📂' : '📄'}
        </div>
        <div className="text-center">
          <p className="text-lg font-semibold text-slate-700 dark:text-slate-200">
            {disabled ? 'Processing...' : 'Drop your claim PDF here'}
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {disabled ? 'Agents are working — this takes 20–60 seconds' : 'or click to browse · PDF only · max 10 MB'}
          </p>
        </div>
        <input ref={inputRef} type="file" accept=".pdf,application/pdf" className="hidden" onChange={e => { handleFile(e.target.files[0]); e.target.value = '' }} disabled={disabled} />
      </div>

      {error && (
        <div className="w-full bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3 text-sm text-red-700 dark:text-red-400 flex items-center gap-2">
          <span>⚠️</span><span>{error}</span>
        </div>
      )}
    </div>
  )
}
