/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2f9f9',
          100: '#deefef',
          500: '#0f766e',
          600: '#0d5f59',
          700: '#0b4f4a'
        }
      }
    }
  },
  plugins: []
}
