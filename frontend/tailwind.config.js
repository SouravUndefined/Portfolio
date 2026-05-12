/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          900: '#080c14',   // deep navy-black
          800: '#0d1220',   // section bg
          700: '#111827',   // card surface
          600: '#1e2a3d',   // hovered card / borders
        },
        ink: {
          0:   '#ffffff',
          200: '#c8d6e8',   // cool white
          400: '#6b7fa0',   // blue-gray muted
          600: '#3d4f6a',   // very muted
        },
        blue: {
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a5f',
        },
        cyan: {
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        },
        rose: {
          400: '#f472b6',
          500: '#ec4899',
        },
        sky: {
          400: '#38bdf8',
          500: '#0ea5e9',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['Syne', 'system-ui', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in':  'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'glow':     'glow 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        glow: {
          '0%, 100%': { boxShadow: '0 0 40px rgba(59, 130, 246, 0.2)' },
          '50%':      { boxShadow: '0 0 60px rgba(59, 130, 246, 0.35)' },
        },
      },
    },
  },
  plugins: [],
}
