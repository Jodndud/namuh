/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{html,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-blue': '#00f0ff',
        'cyber-purple': '#8b5cf6', 
        'cyber-pink': '#ec4899',
      },
    },
  },
  plugins: [],
}
