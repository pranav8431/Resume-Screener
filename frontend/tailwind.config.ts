import type { Config } from 'tailwindcss';

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#000000',
        panel: '#0a0a0a',
        panel2: '#050505',
        line: '#1a1a1a',
        accent: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e'
        }
      },
      boxShadow: {
        soft: '0 20px 60px rgba(0, 0, 0, 0.35)',
        glow: '0 0 0 1px rgba(14, 165, 233, 0.25), 0 16px 48px rgba(14, 165, 233, 0.08)'
      },
      backgroundImage: {
        'hero-grid':
          'radial-gradient(circle at 20% 20%, rgba(14,165,233,0.16), transparent 0), radial-gradient(circle at 80% 0%, rgba(6,182,212,0.14), transparent 0), linear-gradient(180deg, rgba(10,10,10,0.7), rgba(0,0,0,1))'
      },
      borderRadius: {
        'xl2': '1.25rem'
      }
    }
  },
  plugins: []
} satisfies Config;