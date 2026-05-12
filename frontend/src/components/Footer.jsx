import { Github, Linkedin, Instagram, Mail, ArrowUpRight } from 'lucide-react'

const social = [
  { href: 'https://github.com/SouravM47',                     Icon: Github,    label: 'GitHub'    },
  { href: 'https://linkedin.com/in/sourav-mondal-6680b1232',  Icon: Linkedin,  label: 'LinkedIn'  },
  { href: 'https://instagram.com/souravmondal',               Icon: Instagram, label: 'Instagram' },
]

export default function Footer() {
  return (
    <footer id="contact" className="border-t border-white/5 bg-bg-800/20">
      <div className="max-w-6xl mx-auto px-6 pt-20 pb-10">

        <div className="grid md:grid-cols-2 gap-10 items-end mb-16">
          <div>
            <p className="section-label">Contact</p>
            <h2 className="text-3xl md:text-4xl font-display font-bold text-white leading-tight mb-4">
              Let's build something<br />
              <span className="text-ink-400">worth building.</span>
            </h2>
            <p className="text-ink-400 leading-relaxed max-w-sm">
              Have a project in mind or just want to talk AI?
              I reply to every email.
            </p>
          </div>

          <div className="md:self-end md:text-right">
            <a href="mailto:sourav72598@gmail.com"
               className="inline-flex items-center gap-3 px-6 py-3.5 rounded-full
                          bg-blue-500 text-white font-semibold text-sm
                          hover:bg-blue-400 transition-all hover:scale-[1.03]
                          shadow-lg shadow-blue-500/25 group">
              <Mail size={15} strokeWidth={1.5} />
              sourav72598@gmail.com
              <ArrowUpRight size={14} strokeWidth={2}
                            className="opacity-60 group-hover:opacity-100
                                       group-hover:translate-x-0.5 group-hover:-translate-y-0.5
                                       transition-all" />
            </a>
          </div>
        </div>

        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <a href="#home"
             className="font-display font-bold text-white text-lg tracking-tight
                        hover:opacity-70 transition-opacity">
            SM<span className="text-blue-400">.</span>
          </a>

          <div className="flex items-center gap-2">
            {social.map(({ href, Icon, label }) => (
              <a key={label} href={href}
                 target="_blank" rel="noopener noreferrer"
                 aria-label={label}
                 className="w-9 h-9 rounded-lg bg-bg-700 border border-white/5
                            text-ink-400 hover:text-white hover:border-blue-500/40
                            flex items-center justify-center transition-all hover:-translate-y-0.5">
                <Icon size={15} strokeWidth={1.5} />
              </a>
            ))}
          </div>

          <p className="text-ink-600 text-xs">© 2026 Sourav Mondal</p>
        </div>
      </div>
    </footer>
  )
}
