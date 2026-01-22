/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Instrument Sans", "system-ui", "-apple-system", "Segoe UI", "Arial", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Liberation Mono", "monospace"],
      },
      colors: {
        bg: "rgb(var(--c-bg) / <alpha-value>)",
        panel: "rgb(var(--c-panel) / <alpha-value>)",
        panel2: "rgb(var(--c-panel2) / <alpha-value>)",
        text: "rgb(var(--c-text) / <alpha-value>)",
        muted: "rgb(var(--c-muted) / <alpha-value>)",
        border: "rgb(var(--c-border) / <alpha-value>)",
        primary: "rgb(var(--c-primary) / <alpha-value>)",
        primary2: "rgb(var(--c-primary2) / <alpha-value>)",
        cta: "rgb(var(--c-cta) / <alpha-value>)",
        danger: "rgb(var(--c-danger) / <alpha-value>)",
        success: "rgb(var(--c-success) / <alpha-value>)",
        warn: "rgb(var(--c-warn) / <alpha-value>)",
      },
      boxShadow: {
        glow: "0 0 0 1px rgb(255 255 255 / 0.20), 0 24px 80px rgb(2 6 23 / 0.18)",
      },
      borderRadius: {
        xl: "16px",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: 0, transform: "translateY(10px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "0% 0%" },
          "100%": { backgroundPosition: "200% 0%" },
        },
      },
      animation: {
        fadeUp: "fadeUp 420ms cubic-bezier(0.22, 1, 0.36, 1)",
        shimmer: "shimmer 1.2s linear infinite",
      },
    },
  },
  plugins: [],
}
