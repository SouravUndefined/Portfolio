import { useState, useEffect } from 'react'

const links = [
  { href: '#about',   label: 'About'   },
  { href: '#tools',   label: 'Tools'   },
  { href: '#gallery', label: 'Gallery' },
]

export default function Nav() {
  const [scrolled,  setScrolled]  = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 30)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 inset-x-0 z-40 transition-all duration-300
        ${scrolled
          ? 'bg-bg-900/85 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/40'
          : ''}`}
    >
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#home"
           className="font-display font-bold text-white text-lg tracking-tight hover:opacity-75 transition-opacity">
          SM<span className="text-blue-400">.</span>
        </a>

        <nav className="hidden md:flex items-center gap-1">
          {links.map(({ href, label }) => (
            <a key={href} href={href}
               className="px-4 py-2 rounded-lg text-sm text-ink-400 hover:text-white
                          hover:bg-white/5 transition-all">
              {label}
            </a>
          ))}
          <a href="#contact"
             className="ml-3 px-5 py-2 rounded-full border border-white/12 text-ink-200
                        hover:border-blue-500/50 hover:text-white text-sm transition-all
                        hover:bg-blue-500/8">
            Contact
          </a>
        </nav>

        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="md:hidden w-9 h-9 flex flex-col items-center justify-center gap-1.5"
          aria-label="Toggle menu"
        >
          <span className={`block w-5 h-px bg-ink-200 transition-all duration-200 ${menuOpen ? 'rotate-45 translate-y-2' : ''}`} />
          <span className={`block w-5 h-px bg-ink-200 transition-all duration-200 ${menuOpen ? 'opacity-0' : ''}`} />
          <span className={`block w-5 h-px bg-ink-200 transition-all duration-200 ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden bg-bg-800/95 backdrop-blur-xl border-b border-white/5 px-6 py-4 space-y-1">
          {links.map(({ href, label }) => (
            <a key={href} href={href}
               onClick={() => setMenuOpen(false)}
               className="block px-3 py-2.5 rounded-lg text-sm text-ink-200 hover:text-white
                          hover:bg-white/5 transition-all">
              {label}
            </a>
          ))}
          <a href="#contact"
             onClick={() => setMenuOpen(false)}
             className="block px-3 py-2.5 text-sm text-blue-400 font-medium">
            Contact
          </a>
        </div>
      )}
    </header>
  )
}
