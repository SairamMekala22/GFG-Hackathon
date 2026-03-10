/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#050816",
        panel: "#0f172a",
        accent: "#22c55e",
        signal: "#38bdf8",
        ember: "#f59e0b"
      },
      fontFamily: {
        display: ["Sora", "sans-serif"],
        body: ["Manrope", "sans-serif"]
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(148, 163, 184, 0.08), 0 20px 45px rgba(15, 23, 42, 0.35)"
      }
    }
  },
  plugins: []
};
