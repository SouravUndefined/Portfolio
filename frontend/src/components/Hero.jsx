import { Code2, Camera, Sparkles } from 'lucide-react'

export default function Hero() {
  return (
    <section id="home" className="hero-bg relative min-h-screen flex items-center justify-center px-6 pt-20 pb-24">
      {/* Decorative blurred orbs */}
      <div className="absolute top-10 left-10 w-72 h-72 bg-violet-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-80 h-80 bg-rose-600/20 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-3xl text-center animate-fade-in">
        {/* Welcome badge */}
        <div className="pill border-white/10 bg-white/5 text-ink-200 mb-8">
          <Sparkles size={14} className="text-violet-400" />
          Welcome to my digital space
        </div>

        {/* Name */}
        <h1 className="text-6xl md:text-7xl font-bold tracking-tight text-white mb-6">
          Sourav Mondal
        </h1>

        {/* Two clickable role badges */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
          <a href="#tools"
             className="pill border-violet-500/40 bg-violet-600/20 text-violet-200
                        hover:bg-violet-600/30 hover:border-violet-400/60 hover:scale-105 cursor-pointer">
            <Code2 size={14} /> AI Engineer
          </a>

          <span className="text-ink-600">•</span>

          <a href="#gallery"
             className="pill border-emerald-500/40 bg-emerald-600/20 text-emerald-200
                        hover:bg-emerald-600/30 hover:border-emerald-400/60 hover:scale-105 cursor-pointer">
            <Camera size={14} /> Wildlife Photographer
          </a>
        </div>

        {/* Tagline */}
        <p className="text-lg md:text-xl text-ink-200 max-w-2xl mx-auto leading-relaxed mb-10">
          Crafting intelligent systems that push the boundaries of what's possible, while
          capturing the untamed beauty of nature through my lens.
        </p>

        {/* CTAs */}
        <div className="flex flex-wrap items-center justify-center gap-3">
          <a href="#tools"
             className="px-6 py-3 rounded-full bg-gradient-to-r from-violet-600 to-rose-500
                        hover:from-violet-500 hover:to-rose-400 text-white font-medium
                        transition-all hover:scale-105 shadow-lg shadow-violet-600/30
                        inline-flex items-center">
            <span className="font-mono mr-2">&lt;/&gt;</span>
            View Projects
          </a>
          <a href="#contact"
             className="px-6 py-3 rounded-full border border-white/15 hover:border-white/30
                        text-ink-200 hover:text-white font-medium transition-all hover:bg-white/5">
            Contact Me
          </a>
        </div>
      </div>
    </section>
  )
}
