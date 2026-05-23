const API_BASE = process.env.WMS_API_BASE || "http://127.0.0.1:8088";
const WARE_ID = resolveFixtureWareId();
const AUTH = "Basic " + Buffer.from(process.env.WMS_API_AUTH || "admin:admin123", "ascii").toString("base64");
const KEEP_LATEST = Number(process.env.WMS_FIXTURE_KEEP_LATEST || 1);

function resolveFixtureWareId() {
  const configured = process.env.WMS_FIXTURE_WARE_ID;
  const isLocalApi = /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/i.test(API_BASE);
  if (!configured && !isLocalApi) {
    throw new Error("Set WMS_FIXTURE_WARE_ID explicitly when API_BASE is not local.");
  }
  const wareId = Number(configured || 1);
  if (!Number.isInteger(wareId) || wareId <= 0) {
    throw new Error("WMS_FIXTURE_WARE_ID must be a positive non-zero warehouse id.");
  }
  return wareId;
}

async function api(method, url, body) {
  const response = await fetch(`${API_BASE}${url}`, {
    method,
    headers: { Authorization: AUTH, "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = text;
  }
  if (!response.ok) {
    throw new Error(`${method} ${url} failed: ${response.status} ${typeof payload === "string" ? payload : JSON.stringify(payload)}`);
  }
  return payload;
}

function isFixtureCanvas(item) {
  const code = String(item.canvas_code || "").toUpperCase();
  return code.startsWith("FX-") || code.startsWith("TC-");
}

async function main() {
  const canvases = await api("GET", `/api/admin/warehouse-map/warehouses/${WARE_ID}/canvases`);
  const fixtures = canvases
    .filter(isFixtureCanvas)
    .sort((a, b) => Number(b.canvas_id || 0) - Number(a.canvas_id || 0));
  const keep = fixtures.slice(0, Math.max(0, KEEP_LATEST)).map((item) => Number(item.canvas_id));
  const archive = fixtures.filter((item) => !keep.includes(Number(item.canvas_id)));
  const archived = [];
  for (const item of archive) {
    const result = await api("POST", `/api/admin/warehouse-map/canvases/${item.canvas_id}/archive`, {
      reason: "fixture cleanup keeps recent evidence canvas only",
      updated_by: "warehouse-map-fixture-cleanup",
    });
    archived.push({ canvas_id: item.canvas_id, canvas_code: item.canvas_code, result });
  }
  console.log(JSON.stringify({
    ware_id: WARE_ID,
    fixture_count_before: fixtures.length,
    keep_latest: KEEP_LATEST,
    kept_canvas_ids: keep,
    archived_count: archived.length,
    archived,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exit(1);
});
