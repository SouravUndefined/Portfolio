import {
  TrendingUp, ChefHat, PackageSearch, ScanLine,
  ClipboardList, MailCheck, Kanban, FileSearch,
  FileCheck2, ContactRound, AreaChart, Percent,
  ArrowRight, Zap, Building2, Home, Store,
} from 'lucide-react'

const categories = [
  {
    label: 'Corporate Fellows',
    CategoryIcon: Building2,
    tools: [
      {
        title: 'Spending Analyser',
        desc:  'Upload HDFC, SBI, ICICI, Google Pay or PhonePe statements — get categorized transactions, spending patterns, and a 10-page AI-generated PDF report.',
        icon:  TrendingUp,
        live:  true,
        tag:   'Finance',
      },
      {
        title: 'Meeting Summarizer',
        desc:  'Paste meeting transcript or notes — get structured summary, key decisions, and action items with owners.',
        icon:  ClipboardList,
      },
      {
        title: 'Email Assistant',
        desc:  'Turn bullet points into polished professional emails. Adjust tone from formal to casual in one click.',
        icon:  MailCheck,
      },
      {
        title: 'Task Prioritizer',
        desc:  'Dump your to-do list — AI scores each task by urgency and impact and gives you a ranked action plan.',
        icon:  Kanban,
      },
      {
        title: 'Resume Reviewer',
        desc:  'Paste your resume and a job description — get a gap analysis and specific rewrite suggestions.',
        icon:  FileSearch,
      },
    ],
  },
  {
    label: 'Household Bhaiyo aur Behno',
    CategoryIcon: Home,
    tools: [
      {
        title: 'Meal Planner',
        desc:  'Tell it your budget and how many people — get a full week of meals with a ready shopping list.',
        icon:  ChefHat,
      },
      {
        title: 'Home Inventory',
        desc:  'Scan receipts to log appliances and electronics. Get warranty reminders before things expire.',
        icon:  PackageSearch,
      },
      {
        title: 'Bill Scanner',
        desc:  'Photograph any utility or grocery bill — extracts items, totals, and flags suspicious charges.',
        icon:  ScanLine,
      },
    ],
  },
  {
    label: 'Small Business Buddy',
    CategoryIcon: Store,
    tools: [
      {
        title: 'Invoice Generator',
        desc:  'Fill in client details once — get a professional GST-ready PDF invoice in seconds.',
        icon:  FileCheck2,
      },
      {
        title: 'Customer Tracker',
        desc:  'Log client interactions, follow-up dates, and deal status. Never let a lead go cold.',
        icon:  ContactRound,
      },
      {
        title: 'Analytics Dashboard',
        desc:  'Connect your sales data — visualize revenue trends, best products, and slow movers.',
        icon:  AreaChart,
      },
      {
        title: 'GST Calculator',
        desc:  'Enter amount and HSN code — instantly get CGST, SGST, IGST breakdowns and invoice totals.',
        icon:  Percent,
      },
    ],
  },
]

const liveTools = categories.flatMap(c => c.tools.filter(t => t.live))

export default function Tools({ onOpenTool }) {
  return (
    <section id="tools" className="py-32 px-6 bg-bg-800/40">
      <div className="max-w-6xl mx-auto">
        <p className="section-label text-center">Tools</p>
        <h2 className="text-3xl md:text-4xl font-display font-bold text-white text-center mb-3 leading-tight">
          AI tools I'm building
        </h2>
        <p className="text-ink-400 text-center max-w-md mx-auto mb-16">
          Practical utilities that use AI where it genuinely helps — not just for the sake of it.
        </p>

        {/* ── Live Now ──────────────────────────────────────────── */}
        <div className="mb-14">
          <div className="flex items-center gap-3 mb-5">
            <Zap size={14} className="text-emerald-400" strokeWidth={2} />
            <span className="text-sm font-semibold text-emerald-400 tracking-wide">Live now</span>
            <div className="flex-1 h-px bg-bg-600" />
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {liveTools.map((t) => (
              <LiveCard key={t.title} tool={t} onOpen={onOpenTool} />
            ))}
          </div>
        </div>

        {/* ── Categories ───────────────────────────────────────── */}
        <div className="space-y-12">
          {categories.map((cat) => {
            const CatIcon = cat.CategoryIcon
            return (
            <div key={cat.label}>
              <div className="flex items-center gap-3 mb-5">
                <div className="w-6 h-6 rounded-lg bg-white/5 border border-white/10
                                flex items-center justify-center shrink-0">
                  <CatIcon size={12} className="text-ink-300" strokeWidth={1.5} />
                </div>
                <span className="text-sm font-semibold text-ink-200 tracking-wide">{cat.label}</span>
                <div className="flex-1 h-px bg-bg-600" />
              </div>

              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {cat.tools.map((t) =>
                  t.live
                    ? <LiveCard key={t.title} tool={t} onOpen={onOpenTool} compact />
                    : <UpcomingCard key={t.title} tool={t} />
                )}
              </div>
            </div>
          )})}
        </div>
      </div>
    </section>
  )
}

function LiveCard({ tool, onOpen, compact }) {
  const Icon = tool.icon
  return (
    <button onClick={onOpen} className="text-left group w-full">
      <div className={`card border-blue-500/20 h-full
                      hover:border-blue-500/40 hover:-translate-y-0.5
                      transition-all duration-300
                      hover:shadow-xl hover:shadow-blue-500/8
                      bg-gradient-to-br from-bg-700 to-blue-950/20
                      ${compact ? 'p-4' : 'p-5'}`}>
        <div className="flex items-start gap-4">
          <div className={`rounded-xl shrink-0
                          bg-blue-500/12 border border-blue-500/30
                          flex items-center justify-center
                          group-hover:bg-blue-500/20 group-hover:border-blue-400/50
                          transition-all ${compact ? 'w-8 h-8' : 'w-10 h-10'}`}>
            <Icon size={compact ? 14 : 18} className="text-blue-400" strokeWidth={1.5} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1.5">
              <h4 className="text-sm font-semibold text-white">{tool.title}</h4>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full
                               bg-emerald-500/12 text-emerald-400 text-xs font-medium
                               border border-emerald-500/20 shrink-0">
                <span className="w-1 h-1 rounded-full bg-emerald-400
                                 shadow-[0_0_4px_rgba(52,211,153,0.8)]" />
                Live
              </span>
            </div>
            {!compact && (
              <p className="text-ink-400 text-xs leading-relaxed">{tool.desc}</p>
            )}
            <p className={`text-blue-400 text-xs font-semibold inline-flex items-center gap-1.5
                           group-hover:gap-2.5 transition-all ${compact ? 'mt-1' : 'mt-3'}`}>
              Try it now <ArrowRight size={12} strokeWidth={2} />
            </p>
          </div>
        </div>
      </div>
    </button>
  )
}

function UpcomingCard({ tool }) {
  const Icon = tool.icon
  return (
    <div className="card p-4 border-white/5 opacity-60 hover:opacity-85
                    hover:border-blue-500/15 hover:-translate-y-0.5
                    transition-all duration-200 group">
      <div className="w-8 h-8 rounded-xl mb-3
                      bg-white/5 border border-white/10
                      flex items-center justify-center
                      group-hover:bg-blue-500/10 group-hover:border-blue-500/25
                      transition-all">
        <Icon size={14} className="text-ink-400 group-hover:text-blue-400 transition-colors"
              strokeWidth={1.5} />
      </div>
      <h4 className="text-sm font-semibold text-white mb-1">{tool.title}</h4>
      <p className="text-ink-400 text-xs leading-relaxed mb-3">{tool.desc}</p>
      <span className="text-xs text-ink-600 font-medium">Coming soon</span>
    </div>
  )
}
