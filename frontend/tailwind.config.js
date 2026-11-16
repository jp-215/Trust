/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#FAFAF8',
        ink: '#16181D',
        'ink-soft': '#4B4F55',
        'ink-muted': '#6B6F76',
        line: '#E8E6E1',
        'line-faint': '#F0EEEA',
        accent: {
          DEFAULT: '#0E7C66',
          deep: '#0A5C4C',
          tint: '#EDF4F2',
          wash: '#F4F8F6',
          edge: '#DCE8E3',
        },
        warn: {
          DEFAULT: '#92400E',
          tint: '#FDF3E3',
          wash: '#FDF6EA',
          line: '#F3D9B0',
          card: '#FDF9F1',
        },
        danger: '#B42318',
      },
      fontFamily: {
        display: ['var(--font-display)', 'sans-serif'],
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
