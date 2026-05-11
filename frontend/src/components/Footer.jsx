import { Github, Linkedin, Instagram } from 'lucide-react'

export default function Footer() {
  return (
    <footer id="contact" className="border-t border-bg-700 bg-bg-800">
      <div className="max-w-6xl mx-auto px-6 py-10
                      flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <p className="bg-gradient-to-r from-violet-400 to-rose-400 bg-clip-text text-transparent
                        font-bold text-lg">
            Sourav Mondal
          </p>
          <p className="text-ink-400 text-sm">Building the future, one line at a time</p>
        </div>

        <div className="flex items-center gap-3">
          {[
            { href: 'https://github.com/souravmondal63025',     Icon: Github,    label: 'GitHub'    },
            { href: 'https://linkedin.com/in/souravmondal',     Icon: Linkedin,  label: 'LinkedIn'  },
            { href: 'https://instagram.com/souravmondal',       Icon: Instagram, label: 'Instagram' },
          ].map(({ href, Icon, label }) => (
            <a key={label} href={href} target="_blank" rel="noopener noreferrer" aria-label={label}
               className="w-10 h-10 rounded-lg bg-bg-700 border border-bg-600
                          text-ink-400 hover:text-white hover:border-violet-500
                          flex items-center justify-center transition-colors">
              <Icon size={16} />
            </a>
          ))}
        </div>
      </div>

      <p className="text-center text-ink-600 text-xs pb-6">
        © 2026 Sourav Mondal. All rights reserved.
      </p>
    </footer>
  )
}
