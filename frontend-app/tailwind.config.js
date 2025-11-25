/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  // TypeScript 지원을 위한 설정
  future: {
    hoverOnlyWhenSupported: true,
  },
}
