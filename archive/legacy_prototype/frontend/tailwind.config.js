/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#070c14',
          surface: '#0f1724',
          surfaceHover: '#162235',
          card: '#121d2c',
          border: '#1f2e42',
          borderLight: '#2b3f58',
          teal: '#2dd4bf',
          tealDark: '#0f766e',
          mint: '#6ee7b7',
          amber: '#f59e0b',
          rose: '#f43f5e',
          blue: '#3b82f6',
          purple: '#a855f7',
          muted: '#8b9bb4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace']
      }
    },
  },
  plugins: [],
}
