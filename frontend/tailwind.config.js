/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          900: '#0b0d1f',     // deepest body bg
          800: '#11142b',     // section bg
          700: '#181b3a',     // card surface
          600: '#212447',     // hovered card
        },
        ink: {
          0:   '#ffffff',
          200: '#cbd0e6',
          400: '#8e94b8',
          600: '#525775',
        },
        violet: {
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          900: '#3b0764',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        },
        rose: {
          400: '#f472b6',
          500: '#ec4899',
          600: '#db2777',
        },
        sky: {
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in':   'fadeIn 0.6s ease-out forwards',
        'slide-up':  'slideUp 0.6s ease-out forwards',
        'glow':      'glow 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        glow: {
          '0%, 100%': { boxShadow: '0 0 40px rgba(124, 58, 237, 0.25)' },
          '50%':      { boxShadow: '0 0 60px rgba(124, 58, 237, 0.4)' },
        },
      },
    },
  },
  plugins: [],
}
