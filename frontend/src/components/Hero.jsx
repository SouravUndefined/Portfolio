import { ArrowDown } from 'lucide-react'

export default function Hero() {
  return (
    <section id="home" className="hero-bg relative min-h-screen flex flex-col items-center justify-center px-6">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                        w-[900px] h-[500px] bg-blue-700/8 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-cyan-600/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-4xl w-full mx-auto text-center">
        <div className="inline-flex items-center gap-2 mb-10 px-4 py-1.5 rounded-full
                        border border-white/8 bg-white/3 text-xs text-ink-400 tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400
                           shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
          Open to freelance & collaboration
        </div>

        <h1 className="text-[clamp(3.5rem,10vw,6.5rem)] font-display font-extrabold tracking-tight
                       text-white leading-[0.95] mb-8">
          Sourav<br />
          <span className="gradient-text">Mondal</span>
        </h1>

        <div className="flex items-center justify-center gap-3 mb-8 text-sm text-ink-400 font-medium">
          <span>AI Engineer</span>
          <span className="w-1 h-1 rounded-full bg-ink-600" />
          <span>Wildlife Photographer</span>
          <span className="w-1 h-1 rounded-full bg-ink-600" />
          <span>Based in India</span>
        </div>

        <p className="text-ink-400 text-lg max-w-md mx-auto mb-12 leading-relaxed">
          I build AI tools that are actually useful.
          When I'm not coding, I'm in the wild with a camera.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3">
          <a href="#tools"
             className="px-7 py-3 rounded-full bg-blue-500 text-white font-semibold text-sm
                        hover:bg-blue-400 transition-all hover:scale-[1.03]
                        shadow-lg shadow-blue-500/30">
            See my work
          </a>
          <a href="#contact"
             className="px-7 py-3 rounded-full border border-white/12 text-ink-200
                        hover:border-blue-500/40 hover:text-white text-sm font-medium
                        transition-all hover:bg-blue-500/6">
            Get in touch
          </a>
        </div>
      </div>

      <a href="#about"
         className="absolute bottom-10 left-1/2 -translate-x-1/2 text-ink-600
                    hover:text-blue-400 transition-colors animate-bounce">
        <ArrowDown size={20} />
      </a>
    </section>
  )
}
