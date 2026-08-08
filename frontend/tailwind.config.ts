import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#ffffff",
          muted: "#f8fafc",
        },
        content: {
          DEFAULT: "#0f172a",
          muted: "#64748b",
        },
        accent: {
          DEFAULT: "#2563eb",
          hover: "#1d4ed8",
        },
        border: {
          DEFAULT: "#e2e8f0",
        },
      },
    },
  },
  plugins: [],
};

export default config;
