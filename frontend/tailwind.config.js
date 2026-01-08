/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hub-dark': '#1a1a1a',
        'hub-panel': '#252526',
        'hub-accent': '#3b82f6',
        'hub-text': '#e5e7eb',
      }
    },
  },
  plugins: [],
}