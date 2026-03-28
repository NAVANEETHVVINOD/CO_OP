import type { Config } from "tailwindcss";

const config = {
  darkMode: "class",
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        base: 'var(--bg-base)',
        surface: 'var(--bg-surface)',
        elevated: 'var(--bg-elevated)',
        dim: 'var(--border)',
        bright: 'var(--border-bright)',
        accent: {
          DEFAULT: 'var(--accent)',
          hover: 'var(--accent-hover)',
          glow: 'var(--accent-glow)'
        },
        green: 'var(--status-green)',
        red: {
          status: 'var(--status-red)',
          DEFAULT: 'var(--status-red)' // Fallback for simple 'red' usage
        },
        amber: 'var(--status-amber)',
        primary: {
          DEFAULT: 'var(--text-primary)',
        },
        secondary: {
          DEFAULT: 'var(--text-secondary)',
        },
        muted: {
          DEFAULT: 'var(--text-muted)',
        },
      },
      borderColor: {
        dim: 'var(--border)',
        bright: 'var(--border-bright)',
        DEFAULT: 'var(--border)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  plugins: [require("tailwindcss-animate")],
} satisfies Config;

export default config;
