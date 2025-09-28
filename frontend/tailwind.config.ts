import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        space: { 950: "#030014", 900: "#0a0628", 800: "#141044" },
        nebula: "#6d28d9",
        solar: "#22d3ee",
        cosmic: "#a855f7",
      },
      fontFamily: { display: ["Space Grotesk", "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
};
export default config;
