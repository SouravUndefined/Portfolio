// All photos by @Sourav Photography
const photos = [
  { file: 'IMG_5164.JPG.jpeg', alt: 'Blue pit viper — Agumbe forests',     span: 'col-span-1 row-span-2' },
  { file: 'IMG_5172.JPG.jpeg', alt: 'Black-winged stilt wading',           span: 'col-span-2'            },
  { file: 'IMG_5169.JPG.jpeg', alt: 'Painted stork portrait'                                             },
  { file: 'IMG_5179.JPG.jpeg', alt: 'Barn swallow in flight'                                             },
  { file: 'IMG_5168.JPG.jpeg', alt: 'Indian wild boar — Tadoba',           span: 'col-span-2'            },
  { file: 'IMG_5170.JPG.jpeg', alt: 'Green vine snake — night macro'                                     },
  { file: 'IMG_5167.JPG.jpeg', alt: 'Indian cobra — full hood display'                                   },
  { file: 'IMG_5177.JPG.jpeg', alt: 'Tree frog — monsoon night'                                         },
  { file: 'IMG_5175.JPG.jpeg', alt: 'Pied bushchat — forest edge'                                       },
  { file: 'IMG_5174.JPG.jpeg', alt: 'Oriental garden lizard'                                             },
  { file: 'IMG_5178.JPG.jpeg', alt: 'Indian rat snake in rock crevice'                                   },
  { file: 'IMG_5173.JPG.jpeg', alt: 'Long-jawed orb weaver — macro'                                     },
]

export default function Gallery() {
  return (
    <section id="gallery" className="py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <p className="section-label text-center">Photography</p>
        <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-3 leading-tight">
          <span className="gradient-text">Wildlife Gallery</span>
        </h2>
        <p className="text-ink-400 text-center mb-2 max-w-md mx-auto">
          Reptiles, birds, and small creatures across India.
        </p>
        <p className="text-ink-600 text-center text-xs mb-14">© Sourav Photography — all rights reserved</p>

        <div className="grid grid-cols-2 md:grid-cols-4 auto-rows-[180px] gap-3">
          {photos.map((p, i) => (
            <div key={i}
                 className={`relative overflow-hidden rounded-xl group cursor-pointer ${p.span || ''}`}>
              <img
                src={`/gallery/${p.file}`}
                alt={p.alt}
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-700
                           group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/10 to-transparent
                              opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <p className="absolute bottom-3 left-3 right-3 text-white text-xs font-medium
                            opacity-0 group-hover:opacity-100 transition-all duration-300
                            translate-y-1 group-hover:translate-y-0">
                {p.alt}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
