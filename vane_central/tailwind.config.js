/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep navy control-room backgrounds
        'navy-950': '#0A0E27',
        'navy-900': '#0F1335',
        'navy-800': '#141B3D',
        'navy-700': '#1A2142',
        'navy-600': '#252D56',
        // Electric blue primary
        'electric': '#00D4FF',
        'electric-dim': '#0A84FF',
        // Functional colors
        'relay-on': '#00E676',
        'relay-cut': '#FF3D71',
        'relay-warn': '#FFB800',
        // Glass panel colors
        'glass': 'rgba(255, 255, 255, 0.06)',
        'glass-border': 'rgba(255, 255, 255, 0.10)',
      },
      fontFamily: {
        'heading': ['Montserrat', 'sans-serif'],
        'body': ['"Source Sans Pro"', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 40px rgba(0, 212, 255, 0.6)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
