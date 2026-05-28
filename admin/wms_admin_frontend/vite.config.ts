import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";

const projectDefaultsPath = path.resolve(__dirname, "../..", "config", "project.defaults.json");
const projectDefaults = JSON.parse(fs.readFileSync(projectDefaultsPath, "utf8")).local;
const localHost = process.env.TMS_LOCAL_HOST || projectDefaults.loopbackHost;
const frontendPort = Number(process.env.TMS_FRONTEND_PORT || projectDefaults.frontendPort);

export default defineConfig({
  plugins: [react()],
  envPrefix: ["VITE_", "REACT_APP_"],
  server: {
    host: localHost,
    port: frontendPort,
    strictPort: false,
    fs: {
      allow: [path.resolve(__dirname, "../..")]
    }
  },
  preview: {
    host: localHost,
    port: frontendPort
  }
});
