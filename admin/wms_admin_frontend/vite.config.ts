import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  envPrefix: ["VITE_", "REACT_APP_"],
  server: {
    port: 3000,
    strictPort: false,
    fs: {
      allow: [path.resolve(__dirname, "../..")]
    }
  },
  preview: {
    port: 3000
  }
});
