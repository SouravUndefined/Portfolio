import { useState, useRef, useCallback } from 'react'
import {
  Upload, FileText, Loader2, CheckCircle, AlertCircle,
  BarChart2, FileSpreadsheet, RefreshCw, X, Shield, ChevronDown,
} from 'lucide-react'
import ConsentModal from './ConsentModal'

// VITE_API_URL examples:
//   "/api"                            (same-origin EC2 nginx setup)
//   "https://api.yourdomain.com"      (separate API subdomain)
const API_BASE = import.meta.env.VITE_API_URL || ''

const STAGES = {
  IDLE:       'idle',
  PROCESSING: 'processing',
  DONE:       'done',
  ERROR:      'error',
}

const ACCEPTED = /\.(pdf|xlsx|xls|csv)$/i

export default function SpendingTool() {
  const [stage,    setStage]    = useState(STAGES.IDLE)
  const [files,    setFiles]    = useState([])
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState('')
  const [results,  setResults]  = useState(null)
  const [error,    setError]    = useState('')
  const inputRef  = useRef(null)
  const abortRef  = useRef(null)

  const [consentGiven, setConsentGiven] = useState(
    () => sessionStorage.getItem('spending_consent_given') === 'true'
  )
  const handleConsent = () => {
    sessionStorage.setItem('spending_consent_given', 'true')
    setConsentGiven(true)
  }

  const reset = () => {
    abortRef.current?.abort()
    setStage(STAGES.IDLE)
    setFiles([])
    setProgress('')
    setResults(null)
    setError('')
  }

  const addFiles = (fileList) => {
    const incoming = Array.from(fileList)
    const errors = []
    const valid  = []

    incoming.forEach(f => {
      if (!ACCEPTED.test(f.name))          { errors.push(`${f.name}: only PDF / Excel / CSV`); return }
      if (f.size > 15 * 1024 * 1024)       { errors.push(`${f.name}: too large (max 15 MB)`); return }
      valid.push(f)
    })

    if (errors.length) setError(errors.join(' · '))
    else setError('')

    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name))
      return [...prev, ...valid.filter(f => !existing.has(f.name))]
    })
  }

  const removeFile = (name) => setFiles(prev => prev.filter(f => f.name !== name))

  const onDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files)
  }, [])
  const onDragOver  = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = ()  => setDragging(false)

  const startAnalysis = async () => {
    if (!files.length || !API_BASE) {
      setError(!API_BASE ? 'API not configured — see VITE_API_URL in .env.' : 'No files selected.')
      return
    }

    setStage(STAGES.PROCESSING)
    setProgress(`Uploading ${files.length} file${files.length > 1 ? 's' : ''} and analysing… (typically 5–15 min for multi-page PDFs)`)

    const formData = new FormData()
    files.forEach(f => formData.append('files', f))

    abortRef.current = new AbortController()
    const timer = setTimeout(() => abortRef.current.abort(), 20 * 60 * 1000)

    try {
      const res = await fetch(`${API_BASE}/analyse`, {
        method:  'POST',
        body:    formData,
        signal:  abortRef.current.signal,
        headers: { 'X-Consent-Given': 'true' },
      })

      clearTimeout(timer)

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Server returned ${res.status}`)
      }

      const data = await res.json()

      const absolutize = (u) =>
        u.startsWith('http') ? u
          : API_BASE.startsWith('http') ? new URL(u, API_BASE).toString()
          : u

      setResults({
        csvUrl:    absolutize(data.csv_url),
        reportUrl: absolutize(data.report_url),
        rowCount:  data.row_count,
      })
      setStage(STAGES.DONE)

    } catch (err) {
      clearTimeout(timer)
      setError(err.name === 'AbortError'
        ? 'Request timed out after 20 minutes.'
        : err.message)
      setStage(STAGES.ERROR)
    }
  }

  return (
    <div className="card p-8 animate-glow">
      {!consentGiven
        ? <ConsentModal onAccept={handleConsent} onCancel={() => {}} />
        : <>
            {stage === STAGES.IDLE && (
              <Idle files={files} dragging={dragging} error={error} inputRef={inputRef}
                    onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}
                    onChange={e => addFiles(e.target.files)} onRemove={removeFile}
                    onStart={startAnalysis} />
            )}
            {stage === STAGES.PROCESSING && <Processing progress={progress} fileCount={files.length} />}
            {stage === STAGES.DONE       && <Done results={results} fileCount={files.length} onReset={reset} />}
            {stage === STAGES.ERROR      && <ErrorState error={error} onReset={reset} />}
          </>
      }
    </div>
  )
}

/* ── Sub-views ─────────────────────────────────────────────── */

function Idle({ files, dragging, error, inputRef, onDrop, onDragOver, onDragLeave, onChange, onRemove, onStart }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white mb-1">Upload Your Statements</h3>
        <p className="text-ink-400 text-sm">
          Supports Google Pay, HDFC, SBI, ICICI, PhonePe and any UPI/CC PDF.
          Upload multiple statements at once. Processed privately and deleted within 1 hour.
        </p>
      </div>

      {/* Drop zone */}
      <div onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}
           onClick={() => inputRef.current?.click()}
           className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                       transition-all ${dragging
                         ? 'border-violet-400 bg-violet-600/10'
                         : 'border-bg-600 hover:border-violet-500 hover:bg-bg-600/40'}`}>
        <input ref={inputRef} type="file" accept=".pdf,.xlsx,.xls,.csv"
               multiple onChange={onChange} className="hidden" />
        <div className="flex flex-col items-center gap-3 text-ink-400">
          <Upload size={28} className={dragging ? 'text-violet-400' : ''} />
          <p className="font-medium text-sm">
            {files.length > 0 ? 'Drop more files or click to add' : 'Drop PDFs here or click to browse'}
          </p>
          <p className="text-xs">PDF · Excel · CSV &bull; Max 15 MB each &bull; Multiple files supported</p>
        </div>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map(f => (
            <li key={f.name}
                className="flex items-center gap-3 px-3 py-2 rounded-lg bg-bg-700 border border-bg-600">
              <FileText size={16} className="text-violet-400 shrink-0" />
              <span className="text-white text-sm truncate flex-1">{f.name}</span>
              <span className="text-ink-500 text-xs shrink-0">{(f.size / 1024).toFixed(0)} KB</span>
              <button onClick={(e) => { e.stopPropagation(); onRemove(f.name) }}
                      className="text-ink-500 hover:text-rose-400 transition-colors shrink-0">
                <X size={14} />
              </button>
            </li>
          ))}
        </ul>
      )}

      {error && (
        <p className="flex items-center gap-2 text-rose-400 text-sm">
          <AlertCircle size={15} /> {error}
        </p>
      )}

      <button onClick={onStart} disabled={!files.length}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-500
                         hover:from-blue-500 hover:to-cyan-400
                         disabled:opacity-40 disabled:cursor-not-allowed
                         text-white font-semibold rounded-xl
                         transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-blue-600/30">
        Analyse My Spending{files.length > 1 ? ` (${files.length} files)` : ''}
      </button>

      <p className="text-xs text-ink-600 text-center">
        Powered by Llama 4 Scout (Meta) via Groq &bull; 100% open-source AI
      </p>

      <details className="rounded-xl border border-bg-600 overflow-hidden text-left">
        <summary className="flex items-center justify-between px-4 py-3 cursor-pointer
                            text-xs text-ink-400 hover:text-ink-200 select-none
                            bg-bg-700 hover:bg-bg-600 transition-colors list-none">
          <span className="flex items-center gap-2">
            <Shield size={12} className="text-blue-400" />
            Privacy &amp; Data Processing Details
          </span>
          <ChevronDown size={12} />
        </summary>
        <div className="px-4 py-4 bg-bg-800 text-xs text-ink-400 space-y-2.5 leading-relaxed">
          <p><strong className="text-ink-200">What is processed:</strong> PDF pages are rendered as images in memory and sent to Groq's API. No raw PDF bytes leave this server — only page images.</p>
          <p><strong className="text-ink-200">Third-party processor:</strong> Groq Cloud (US) runs Meta's Llama 4 Scout vision model. See their{' '}
            <a href="https://groq.com/privacy-policy" target="_blank" rel="noopener noreferrer"
               className="text-blue-400 hover:underline">Privacy Policy</a>.
          </p>
          <p><strong className="text-ink-200">Retention:</strong> Source files deleted immediately after extraction. CSV and PDF report deleted automatically after 1 hour.</p>
          <p><strong className="text-ink-200">No identity linkage:</strong> No user accounts, no cookies, no analytics. Each job gets a random UUID with no association to you.</p>
          <p><strong className="text-ink-200">India DPDPA 2023:</strong> Data is processed only for the purpose you consented to and deleted automatically. You have the right to not use this tool if you do not consent.</p>
        </div>
      </details>
    </div>
  )
}

function Processing({ progress, fileCount }) {
  return (
    <div className="flex flex-col items-center gap-6 py-8 text-center">
      <Loader2 size={48} className="text-violet-400 animate-spin" />
      <div>
        <p className="text-white font-semibold text-lg mb-2">Analysing…</p>
        <p className="text-ink-400 text-sm max-w-xs">{progress}</p>
      </div>
      <div className="w-full bg-bg-600 rounded-full h-1.5 max-w-xs overflow-hidden">
        <div className="bg-gradient-to-r from-violet-500 to-rose-400 h-1.5 rounded-full
                        animate-pulse w-2/3" />
      </div>
      <p className="text-xs text-ink-600">
        {fileCount > 1
          ? `Processing ${fileCount} files — the AI reads each page like a human.`
          : 'The AI reads each page like a human — large PDFs take 1–2 minutes.'}
      </p>
    </div>
  )
}

function Done({ results, fileCount, onReset }) {
  return (
    <div className="flex flex-col items-center gap-6 py-4 text-center">
      <CheckCircle size={52} className="text-emerald-400" />
      <div>
        <h3 className="text-xl font-bold text-white mb-1">Analysis Complete!</h3>
        <p className="text-ink-400 text-sm">
          Processed{' '}
          <span className="text-white">
            {fileCount} file{fileCount > 1 ? 's' : ''}
          </span>
          {results?.rowCount ? ` · ${results.rowCount} transactions` : ''}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 w-full">
        <a href={results?.csvUrl} download
           className="flex flex-col items-center gap-2 p-4 card
                      hover:border-violet-500 transition-all hover:-translate-y-0.5">
          <FileSpreadsheet size={28} className="text-violet-400" />
          <span className="text-sm font-medium text-white">Download CSV</span>
          <span className="text-xs text-ink-400">Power BI ready &bull; 31 columns</span>
        </a>
        <a href={results?.reportUrl} download
           className="flex flex-col items-center gap-2 p-4 card
                      hover:border-sky-500 transition-all hover:-translate-y-0.5">
          <BarChart2 size={28} className="text-sky-400" />
          <span className="text-sm font-medium text-white">Download Report</span>
          <span className="text-xs text-ink-400">10-page AI PDF report</span>
        </a>
      </div>

      <button onClick={onReset}
              className="flex items-center gap-2 text-ink-400 hover:text-white
                         text-sm font-medium transition-colors mt-2">
        <RefreshCw size={14} /> Analyse another file
      </button>
    </div>
  )
}

function ErrorState({ error, onReset }) {
  return (
    <div className="flex flex-col items-center gap-5 py-8 text-center">
      <AlertCircle size={48} className="text-rose-400" />
      <div>
        <h3 className="text-lg font-bold text-white mb-1">Something went wrong</h3>
        <p className="text-ink-400 text-sm max-w-xs">{error}</p>
      </div>
      <button onClick={onReset}
              className="flex items-center gap-2 px-5 py-2.5 bg-bg-600 hover:bg-bg-700
                         text-white rounded-xl text-sm font-medium transition-colors">
        <RefreshCw size={14} /> Try again
      </button>
    </div>
  )
}
