import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [react()],
  build: { rollupOptions: { input: {
    terminal: fileURLToPath(new URL("./index.html", import.meta.url)),
    store: fileURLToPath(new URL("./store/index.html", import.meta.url)),
    assembly: fileURLToPath(new URL("./assembly/index.html", import.meta.url)),
    caseWork: fileURLToPath(new URL("./case-work/index.html", import.meta.url))
  } } },
  envPrefix: ["VITE_", "REACT_APP_"],
  server: {
    proxy: {
      "/api": { target: "http://127.0.0.1:8088", changeOrigin: false },
      "/help": { target: "http://127.0.0.1:8088", changeOrigin: false },
      "/wms-admin": { target: "http://127.0.0.1:8088", changeOrigin: false }
    },
    port: 3010,
    strictPort: false
  },
  preview: {
    port: 3010
  }
});
