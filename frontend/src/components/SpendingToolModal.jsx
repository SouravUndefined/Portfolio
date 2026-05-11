import { useEffect } from 'react'
import { X, Wallet } from 'lucide-react'
import SpendingTool from './SpendingTool'

export default function SpendingToolModal({ open, onClose }) {
  // Close on Escape key + lock body scroll while open
  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', onKey)
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm
                 flex items-start justify-center overflow-y-auto p-4 md:p-8 animate-fade-in">
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-2xl my-8">

        {/* Header strip */}
        <div className="flex items-center justify-between mb-4 px-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
              <Wallet size={18} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Budget Tracker</h3>
              <p className="text-ink-400 text-xs">Personal Spending Analyser &bull; Live</p>
            </div>
          </div>
          <button onClick={onClose}
                  aria-label="Close"
                  className="w-9 h-9 rounded-lg bg-bg-700 hover:bg-bg-600 border border-bg-600
                             text-ink-200 hover:text-white flex items-center justify-center transition-colors">
            <X size={18} />
          </button>
        </div>

        <SpendingTool />
      </div>
    </div>
  )
}
