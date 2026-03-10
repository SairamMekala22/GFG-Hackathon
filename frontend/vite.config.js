import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          recharts: ["recharts"],
          layout: ["react-grid-layout", "react-resizable"],
          export: ["html2canvas", "jspdf"],
          socket: ["socket.io-client"],
          ui: ["lucide-react"]
        }
      }
    }
  },
  server: {
    port: 5173
  }
});
