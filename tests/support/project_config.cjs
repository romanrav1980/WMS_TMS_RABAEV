const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const CONFIG_PATH = path.join(ROOT, "config", "project.defaults.json");

function readDefaults() {
  return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
}

function localConfig() {
  const local = readDefaults().local;
  const host = process.env.TMS_LOCAL_HOST || local.loopbackHost;
  const frontendPort = Number(process.env.TMS_FRONTEND_PORT || local.frontendPort);
  const apiPort = Number(process.env.TMS_API_PORT || local.apiPort);
  return {
    host,
    frontendPort,
    apiPort,
    frontendBaseUrl: process.env.TMS_FRONTEND_BASE_URL || `http://${host}:${frontendPort}`,
    apiBaseUrl: process.env.TMS_API_BASE_URL || process.env.WMS_API_BASE || `http://${host}:${apiPort}`,
  };
}

function pageUrl(page) {
  return `${localConfig().frontendBaseUrl}/?page=${page}`;
}

module.exports = { localConfig, pageUrl };
