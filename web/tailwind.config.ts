import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: "#FAF8F3",
          warm: "#F5F0E8",
          ruled: "#E8E2D6",
          deep: "#EDE8DD",
        },
        ink: {
          DEFAULT: "#2C2C2C",
          light: "#6B6560",
          faint: "#A39E96",
          blue: "#1B4B8A",
          red: "#C13628",
          teal: "#1A7A6D",
          amber: "#B8860B",
        },
        pencil: "#8B8680",
      },
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "serif"],
        sans: ["Source Sans 3", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        "card-hover": "0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)",
        page: "2px 2px 8px rgba(0,0,0,0.05)",
      },
      animation: {
        "spring-in": "springIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards",
        "ink-flow": "inkFlow 0.6s ease-out forwards",
        "page-turn": "pageTurn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)",
        "pencil-write": "pencilWrite 1.2s ease-in-out infinite",
        "pendulum": "pendulum 3s ease-in-out infinite",
        "settle": "settle 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards",
      },
      keyframes: {
        springIn: {
          "0%": { transform: "scale(0.9) translateY(8px)", opacity: "0" },
          "60%": { transform: "scale(1.02) translateY(-2px)", opacity: "1" },
          "100%": { transform: "scale(1) translateY(0)", opacity: "1" },
        },
        inkFlow: {
          "0%": { width: "0%", opacity: "0.3" },
          "100%": { width: "100%", opacity: "1" },
        },
        pageTurn: {
          "0%": { transform: "rotateY(-5deg) scale(0.98)", opacity: "0.7" },
          "100%": { transform: "rotateY(0deg) scale(1)", opacity: "1" },
        },
        pencilWrite: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
        pendulum: {
          "0%, 100%": { transform: "rotate(-3deg)" },
          "50%": { transform: "rotate(3deg)" },
        },
        settle: {
          "0%": { transform: "translateY(-4px)", opacity: "0" },
          "70%": { transform: "translateY(1px)" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      borderRadius: {
        paper: "3px",
      },
    },
  },
  plugins: [],
};

export default config;
