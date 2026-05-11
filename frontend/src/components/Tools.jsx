import {
  Wallet, Utensils, Home,
  FileText, Mail, CheckSquare,
  Receipt, Users, BarChart3,
  ArrowRight,
} from 'lucide-react'

const categories = [
  {
    name: 'Household Bhaiyo aur behno',
    color: 'text-emerald-400',
    tools: [
      {
        title: 'Meal Planner',
        desc:  'Plan your weekly meals and generate shopping lists automatically.',
        icon:  Utensils,
        bg:    'bg-rose-500',
      },
      {
        title: 'Home Inventory',
        desc:  'Keep track of all your household items and their warranties.',
        icon:  Home,
        bg:    'bg-sky-500',
      },
    ],
  },
  {
    name: 'Corporate Fellows',
    color: 'text-rose-400',
    tools: [
      {
        title: 'Budget Tracker',
        desc:  'Track your daily expenses and monthly budgets with ease.',
        icon:  Wallet,
        bg:    'bg-emerald-500',
        live:  true,
      },
      {
        title: 'Meeting Summarizer',
        desc:  'AI-powered tool to summarize meeting notes and action items.',
        icon:  FileText,
        bg:    'bg-violet-500',
      },
      {
        title: 'Email Assistant',
        desc:  'Generate professional email responses with AI suggestions.',
        icon:  Mail,
        bg:    'bg-violet-500',
      },
      {
        title: 'Task Prioritizer',
        desc:  'Smart task management with priority recommendations.',
        icon:  CheckSquare,
        bg:    'bg-emerald-500',
      },
    ],
  },
  {
    name: 'Small Business Buddy',
    color: 'text-sky-400',
    tools: [
      {
        title: 'Invoice Generator',
        desc:  'Create professional invoices in seconds.',
        icon:  Receipt,
        bg:    'bg-violet-500',
      },
      {
        title: 'Customer Tracker',
        desc:  'Manage customer relationships and follow-ups.',
        icon:  Users,
        bg:    'bg-rose-500',
      },
      {
        title: 'Analytics Dashboard',
        desc:  'Visualize your business metrics and growth trends.',
        icon:  BarChart3,
        bg:    'bg-sky-500',
      },
    ],
  },
]

export default function Tools({ onOpenTool }) {
  return (
    <section id="tools" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-3">
          AI-Powered Tools
        </h2>
        <p className="text-ink-400 text-center max-w-xl mx-auto mb-14">
          Intelligent utilities I'm building to make everyday tasks smarter and more efficient.
        </p>

        <div className="space-y-12">
          {categories.map((cat) => (
            <div key={cat.name}>
              <h3 className={`text-center text-sm font-semibold mb-6 ${cat.color}`}>
                {cat.name}
              </h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {cat.tools.map((t) => (
                  <ToolCard key={t.title} tool={t} onOpenTool={onOpenTool} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function ToolCard({ tool, onOpenTool }) {
  const Icon = tool.icon
  const live = tool.live

  const Wrapper = live ? 'button' : 'div'
  const wrapperProps = live
    ? {
        onClick: onOpenTool,
        type:    'button',
        className: 'w-full text-left',
      }
    : {}

  return (
    <Wrapper {...wrapperProps}>
      <article className={`card p-5 h-full transition-all duration-300
        ${live
          ? 'cursor-pointer hover:-translate-y-1 hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-600/20'
          : 'opacity-95'
        }`}>
        <div className={`w-10 h-10 rounded-lg ${tool.bg} flex items-center justify-center mb-4`}>
          <Icon size={18} className="text-white" />
        </div>

        <h4 className="text-base font-semibold text-white mb-2">{tool.title}</h4>
        <p className="text-ink-400 text-xs leading-relaxed mb-4 line-clamp-3">{tool.desc}</p>

        {live ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
                           bg-emerald-500/20 text-emerald-400 text-xs font-medium border border-emerald-500/30">
            Live <ArrowRight size={11} />
          </span>
        ) : (
          <span className="inline-flex px-2.5 py-1 rounded-full
                           bg-violet-500/15 text-violet-400 text-xs font-medium border border-violet-500/25">
            Coming Soon
          </span>
        )}
      </article>
    </Wrapper>
  )
}
