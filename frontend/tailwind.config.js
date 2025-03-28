/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-blue': '#00ffff',
        'neon-pink': '#ff00ff',
        'neon-green': '#00ff00',
        'neon-red': '#ff0000',
      },
      boxShadow: {
        'neon-blue': '0 0 15px rgba(0, 255, 255, 0.5)',
        'neon-pink': '0 0 15px rgba(255, 0, 255, 0.5)',
        'neon-green': '0 0 15px rgba(0, 255, 0, 0.5)',
        'neon-red': '0 0 15px rgba(255, 0, 0, 0.5)',
      },
    },
  },
  plugins: [],
} 