import { Code2, Camera } from 'lucide-react'

export default function About() {
  return (
    <section id="about" className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
          About Me
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          {/* AI Engineering card */}
          <article className="card p-6 border-violet-500/20 hover:border-violet-500/40
                              hover:-translate-y-1 transition-all duration-300 group">
            <div className="w-11 h-11 rounded-xl bg-violet-600 flex items-center justify-center mb-4
                            group-hover:scale-110 transition-transform">
              <Code2 size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-bold text-white mb-3">AI Engineering</h3>
            <p className="text-ink-400 text-sm leading-relaxed">
              Specializing in cutting-edge machine learning solutions that
              transform complex problems into elegant code. From NLP to
              computer vision, I build systems that learn, adapt, and
              deliver real-world impact.
            </p>
          </article>

          {/* Wildlife Photography card */}
          <article className="card p-6 border-emerald-500/20 hover:border-emerald-500/40
                              hover:-translate-y-1 transition-all duration-300 group
                              bg-gradient-to-br from-bg-700 to-emerald-900/20">
            <div className="w-11 h-11 rounded-xl bg-emerald-600 flex items-center justify-center mb-4
                            group-hover:scale-110 transition-transform">
              <Camera size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-bold text-white mb-3">Wildlife Photography</h3>
            <p className="text-ink-400 text-sm leading-relaxed">
              Beyond the screen, I chase moments in the wild — capturing
              the raw beauty and stories of nature. Each photograph is a
              testament to patience, observation, and a deep respect for
              the natural world.
            </p>
          </article>
        </div>
      </div>
    </section>
  )
}
