// Replace these placeholder URLs with your own wildlife photographs.
// Format: 600x400 cropped JPGs from Unsplash.
const photos = [
  { url: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=600&h=400&fit=crop', alt: 'Sunset zebra silhouette' },
  { url: 'https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=600&h=400&fit=crop',  alt: 'Lion portrait'         },
  { url: 'https://images.unsplash.com/photo-1503919005314-30d93d07d823?w=600&h=400&fit=crop', alt: 'Elephant family'        },
  { url: 'https://images.unsplash.com/photo-1605552055839-1f85b6e82d8d?w=600&h=400&fit=crop', alt: 'Bengal tiger'           },
  { url: 'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=600&h=400&fit=crop',  alt: 'Cheetah on grass'       },
  { url: 'https://images.unsplash.com/photo-1611689037739-7a8be5527e58?w=600&h=400&fit=crop', alt: 'Eagle close-up'         },
  { url: 'https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=600&h=400&fit=crop',  alt: 'African savanna sunset' },
  { url: 'https://images.unsplash.com/photo-1551269901-5c5e14c25df7?w=600&h=400&fit=crop',  alt: 'Pink horizon herd'      },
  { url: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=600&h=400&fit=crop', alt: 'Crowned crane'          },
  { url: 'https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=600&h=400&fit=crop', alt: 'Red fox'                },
  { url: 'https://images.unsplash.com/photo-1480044965905-02098d419e96?w=600&h=400&fit=crop', alt: 'Dragonfly macro'        },
  { url: 'https://images.unsplash.com/photo-1458966480358-a0ac42de0a7a?w=600&h=400&fit=crop', alt: 'Birds at the water'     },
]

export default function Gallery() {
  return (
    <section id="gallery" className="py-24 px-6 bg-bg-800">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-3">
          <span className="bg-gradient-to-r from-emerald-400 to-amber-400 bg-clip-text text-transparent">
            Wildlife Photography Gallery
          </span>
        </h2>
        <p className="text-ink-400 text-center mb-14">
          A curated collection of my adventures in the wild, frozen in time.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {photos.map((p, i) => (
            <div key={i}
                 className="relative overflow-hidden rounded-xl aspect-[3/2] group cursor-pointer">
              <img src={p.url} alt={p.alt} loading="lazy"
                   className="w-full h-full object-cover transition-transform duration-500
                              group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent
                              opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <p className="absolute bottom-3 left-3 right-3 text-white text-xs font-medium
                            opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                {p.alt}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
