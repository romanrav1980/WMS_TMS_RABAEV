import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// API ТМС по умолчанию слушает порт из config/project.defaults.json (local.apiPort = 8088).
const apiTarget = process.env.TMS_API_URL ?? "http://127.0.0.1:8088";

export default defineConfig({
  base: "./",
  plugins: [react()],
  server: {
    port: 5181,
    proxy: { "/api": { target: apiTarget, changeOrigin: true } }
  },
  preview: { port: 5181 },
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          three: ["three"],
          r3f: ["@react-three/fiber", "@react-three/drei"]
        }
      }
    }
  }
});
