/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        sans: ['Outfit', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: {
          50: '#f7f6f4',
          100: '#edebe6',
          200: '#d9d5cc',
          300: '#c2bcae',
          400: '#a89f8d',
          500: '#8f8572',
          600: '#7a6f5d',
          700: '#63594a',
          800: '#524a3e',
          900: '#453f36',
          950: '#252219',
        },
        copper: {
          400: '#d4a574',
          500: '#c4915c',
          600: '#a87548',
          700: '#8b5e3c',
          800: '#734e33',
        },
        sage: {
          400: '#9cb39a',
          500: '#7a9b77',
          600: '#5f7d5c',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(37, 34, 25, 0.08), 0 2px 8px -2px rgba(37, 34, 25, 0.04)',
        'card': '0 8px 30px -6px rgba(37, 34, 25, 0.12)',
        'card-hover': '0 16px 40px -8px rgba(37, 34, 25, 0.15)',
      },
    },
  },
  plugins: [],
}
