import { useState }     from 'react'
import Nav              from './components/Nav'
import Hero             from './components/Hero'
import About            from './components/About'
import Tools            from './components/Tools'
import Gallery          from './components/Gallery'
import Footer           from './components/Footer'
import SpendingToolModal from './components/SpendingToolModal'

export default function App() {
  const [toolOpen, setToolOpen] = useState(false)

  return (
    <div className="min-h-screen">
      <Nav />
      <main>
        <Hero />
        <About />
        <Tools  onOpenTool={() => setToolOpen(true)} />
        <Gallery />
      </main>
      <Footer />
      <SpendingToolModal open={toolOpen} onClose={() => setToolOpen(false)} />
    </div>
  )
}
