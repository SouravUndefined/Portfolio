const stats = [
  { value: '3+',   label: 'Years building AI systems'    },
  { value: '10+',  label: 'Tools shipped to production'  },
  { value: '500K', label: 'Groq tokens/day, always free' },
  { value: '∞',    label: 'Photos still left to take'    },
]

export default function About() {
  return (
    <section id="about" className="py-32 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="grid md:grid-cols-5 gap-12 lg:gap-16 items-start">

          {/* Left — profile photo */}
          <div className="md:col-span-2">
            <div className="relative rounded-2xl overflow-hidden aspect-square">
              <img
                src="/gallery/IMG_5176.JPG.jpeg"
                alt="Sourav Mondal"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-bg-900/60 to-transparent" />
            </div>
            <div className="grid grid-cols-2 gap-2.5 mt-2.5">
              {stats.map(({ value, label }) => (
                <div key={label}
                     className="card p-4 border-white/5 hover:border-blue-500/25 transition-colors">
                  <p className="text-xl font-display font-bold text-white mb-1">{value}</p>
                  <p className="text-ink-400 text-xs leading-snug">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right — text */}
          <div className="md:col-span-3 md:pt-2">
            <p className="section-label">About</p>
            <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-6 leading-tight">
              I build AI systems that solve<br />
              <span className="text-ink-400">real problems for real people.</span>
            </h2>
            <div className="space-y-4 text-ink-400 leading-relaxed">
              <p>
                I specialize in LLM applications, document understanding, and AI-powered
                automation. My focus is on shipping things that are genuinely useful —
                not just technically impressive demos.
              </p>
              <p>
                The Spending Analyser below is a good example: upload a bank statement,
                get a detailed breakdown in minutes, powered by open-source AI at zero cost.
              </p>
              <p>
                Away from code, I photograph wildlife — mostly reptiles, birds, and small
                creatures across India. The patience it demands transfers surprisingly
                well to debugging.
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  )
}
