import { useState } from 'react'
import { Shield, AlertCircle } from 'lucide-react'

const CHECKBOXES = [
  {
    id: 'c1',
    text: (
      <>
        I understand that pages of my bank statement PDF will be converted to images and sent to{' '}
        <strong className="text-white">Groq</strong> (a US-based AI company) for text extraction
        using Meta's Llama 4 Scout model.
      </>
    ),
  },
  {
    id: 'c2',
    text: (
      <>
        I understand that my uploaded files are{' '}
        <strong className="text-white">deleted immediately</strong> after processing, and the
        generated CSV and PDF report are{' '}
        <strong className="text-white">permanently deleted within 1 hour</strong>. No data is
        linked to my identity.
      </>
    ),
  },
  {
    id: 'c3',
    text: (
      <>
        I <strong className="text-white">consent</strong> to this processing for the sole purpose
        of generating my personal spending analysis report.
      </>
    ),
  },
]

export default function ConsentModal({ onAccept, onCancel }) {
  const [checked, setChecked] = useState({ c1: false, c2: false, c3: false })

  const allChecked = Object.values(checked).every(Boolean)

  const toggle = (id) => setChecked(prev => ({ ...prev, [id]: !prev[id] }))

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-blue-500/15">
          <Shield size={20} className="text-blue-400" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">Data Processing Consent</h3>
          <p className="text-ink-400 text-xs">Please review before uploading your bank statement</p>
        </div>
      </div>

      {/* Info box */}
      <div className="bg-blue-950/40 border border-blue-500/20 rounded-xl p-4 space-y-2">
        <p className="text-xs font-semibold text-blue-300 mb-2 flex items-center gap-1.5">
          <AlertCircle size={12} /> What happens to your data
        </p>
        {[
          'PDF pages are rendered as images and sent to Groq\'s API for AI-powered transaction extraction.',
          'Source files are deleted immediately after processing. Results (CSV + report) are deleted after 1 hour.',
          'No user accounts, no cookies, no tracking — each job gets a random ID with no link to you.',
        ].map((point, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="text-blue-400 mt-0.5 shrink-0 text-xs">•</span>
            <p className="text-ink-400 text-xs leading-relaxed">{point}</p>
          </div>
        ))}
      </div>

      {/* Checkboxes */}
      <div className="space-y-3">
        {CHECKBOXES.map(({ id, text }) => (
          <label key={id}
                 className="flex items-start gap-3 cursor-pointer group"
                 onClick={() => toggle(id)}>
            <div className={`mt-0.5 w-4 h-4 shrink-0 rounded border flex items-center justify-center
                            transition-colors
                            ${checked[id]
                              ? 'bg-blue-500 border-blue-500'
                              : 'border-bg-500 bg-bg-700 group-hover:border-blue-400'}`}>
              {checked[id] && (
                <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                  <path d="M1 4l3 3 5-6" stroke="white" strokeWidth="1.8"
                        strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </div>
            <p className="text-ink-400 text-xs leading-relaxed group-hover:text-ink-200 transition-colors">
              {text}
            </p>
          </label>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-1">
        <button onClick={onCancel}
                className="flex-1 py-2.5 bg-bg-700 hover:bg-bg-600 border border-bg-500
                           text-ink-300 hover:text-white rounded-xl text-sm font-medium
                           transition-colors">
          Cancel
        </button>
        <button onClick={onAccept} disabled={!allChecked}
                className="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500
                           hover:from-blue-500 hover:to-cyan-400
                           disabled:opacity-40 disabled:cursor-not-allowed
                           text-white font-semibold rounded-xl text-sm
                           transition-all hover:shadow-lg hover:shadow-blue-600/30">
          I Agree &amp; Continue →
        </button>
      </div>
    </div>
  )
}
