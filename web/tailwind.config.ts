import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#050811",
        surface: {
          50: "#0F172A",
          100: "#0B1322",
          200: "#080E1A",
          300: "#050811",
        },
        quantum: {
          cyan: "#00F0FF",
          gold: "#FFB800",
          green: "#00FF9D",
          coral: "#FF3366",
          violet: "#9D4EDD",
          dimCyan: "rgba(0, 240, 255, 0.12)",
          dimGreen: "rgba(0, 255, 157, 0.12)",
        },
        hud: {
          border: "rgba(0, 240, 255, 0.22)",
          subtle: "rgba(140, 155, 176, 0.2)",
          text: "#E2EDF8",
          muted: "#7E92A8",
        },
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        sans: ["Plus Jakarta Sans", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "quantum-spin": "spin 20s linear infinite",
        "wave-drift": "waveDrift 8s linear infinite",
        "glow-ping": "glowPing 2s cubic-bezier(0, 0, 0.2, 1) infinite",
      },
      keyframes: {
        waveDrift: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        glowPing: {
          "0%": { transform: "scale(1)", opacity: "0.8" },
          "100%": { transform: "scale(1.6)", opacity: "0" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
