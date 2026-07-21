/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          deep: '#050505',
          card: 'rgba(15, 15, 15, 0.6)',
        },
        border: {
          subtle: 'rgba(255, 255, 255, 0.08)',
          highlight: 'rgba(255, 255, 255, 0.15)',
        },
        accent: {
          violet: '#7c3aed',
          cyan: '#06b6d4',
        },
      },
      fontFamily: {
        sans: ['Geist Sans', 'Inter', 'sans-serif'],
        mono: ['Geist Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
