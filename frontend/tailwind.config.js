/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        aitema: {
          navy: '#0f172a',
          blue: '#1e3a5f',
          accent: '#3b82f6',
          'accent-hover': '#2563eb',
          emerald: '#059669',
          'slate-50': '#f8fafc',
          'slate-100': '#f1f5f9',
          'slate-200': '#e2e8f0',
          text: '#0f172a',
          muted: '#64748b',
        },
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'aitema-sm': '0 1px 2px rgba(0,0,0,0.05)',
        'aitema-md': '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
        'aitema-lg': '0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)',
        'aitema-xl': '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
      },
      borderRadius: {
        'aitema-card': '0.5rem',
        'aitema-btn': '0.375rem',
        'aitema-modal': '1rem',
      },
      backgroundImage: {
        'aitema-gradient': 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #1e40af 100%)',
        'aitema-gradient-subtle': 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
