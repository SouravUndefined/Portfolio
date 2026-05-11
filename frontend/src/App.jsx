import { useState }      from 'react'
import Hero               from './components/Hero'
import About              from './components/About'
import Tools              from './components/Tools'
import Gallery            from './components/Gallery'
import Footer             from './components/Footer'
import SpendingToolModal  from './components/SpendingToolModal'

export default function App() {
  const [toolOpen, setToolOpen] = useState(false)
  const openTool  = () => setToolOpen(true)
  const closeTool = () => setToolOpen(false)

  return (
    <div className="min-h-screen">
      <main>
        <Hero />
        <About />
        <Tools   onOpenTool={openTool} />
        <Gallery />
      </main>
      <Footer />

      <SpendingToolModal open={toolOpen} onClose={closeTool} />
    </div>
  )
}
