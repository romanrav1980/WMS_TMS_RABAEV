const API_BASE = process.env.WMS_API_BASE || "http://127.0.0.1:8088";
const WARE_ID = resolveFixtureWareId();
const AUTH = "Basic " + Buffer.from(process.env.WMS_API_AUTH || "admin:admin123", "ascii").toString("base64");
const RUN_ID = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);

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

const GRID = { aisle_count: 4, slots_per_aisle: 4, levels: 1 };
const ROLE_ORDER = ["PICK_FACE", "STORAGE", "TRANSPORT_STAGING", "FILM_WRAP", "GATE", "AISLE", "BLOCKED", "EMPTY", "FRACTIONAL_PICK_FACE", "FRACTIONAL_STORAGE"];
const ROLE = Object.fromEntries(ROLE_ORDER.map((role, index) => [role, index]));

function cellIndex(aisle, slot, level) {
  return (level - 1) * GRID.aisle_count * GRID.slots_per_aisle
    + (slot - 1) * GRID.aisle_count
    + (aisle - 1);
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

function assertSame(name, left, right) {
  if (String(left) !== String(right)) {
    throw new Error(`${name}: expected ${left} to equal ${right}`);
  }
}

async function main() {
  const roles = new Uint8Array(GRID.aisle_count * GRID.slots_per_aisle * GRID.levels);
  roles.fill(ROLE.BLOCKED);
  roles[cellIndex(1, 1, 1)] = ROLE.PICK_FACE;
  roles[cellIndex(2, 1, 1)] = ROLE.STORAGE;
  roles[cellIndex(3, 1, 1)] = ROLE.AISLE;
  roles[cellIndex(4, 1, 1)] = ROLE.GATE;

  const idempotency = {
    canvas: `IDEMP-${RUN_ID}-CANVAS`,
    topology: `IDEMP-${RUN_ID}-TOPOLOGY`,
    route: `IDEMP-${RUN_ID}-ROUTE`,
    publish: `IDEMP-${RUN_ID}-PUBLISH`,
  };

  const draft = await api("POST", "/api/admin/warehouse-map-drafts", {
    draft_name: `Idempotency smoke ${RUN_ID}`,
    grid: GRID,
    roles_base64: Buffer.from(roles).toString("base64"),
    created_by: "warehouse-map-idempotency-smoke",
  });

  const route = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/route/build`, {
    selection: { aisle_from: 1, aisle_to: 4, slot_from: 1, slot_to: 1, level_from: 1, level_to: 1 },
    route_code: `IDEMP-ROUTE-${RUN_ID}`,
    route_name: `Idempotency Route ${RUN_ID}`,
    route_pattern: "LINEAR",
    start_sequence: 1,
    step: 1,
    updated_by: "warehouse-map-idempotency-smoke",
  });
  if (route.route_row_count !== 1) {
    throw new Error(`Route smoke expected 1 row, got ${route.route_row_count}`);
  }

  const validation = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/validate`);
  if (!validation.valid) {
    throw new Error(`Draft validation failed: ${JSON.stringify(validation.errors || [])}`);
  }

  const canvas = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/save-to-db`, {
    ware_id: WARE_ID,
    canvas_code: `IDEMP-CANVAS-${RUN_ID}`,
    canvas_name: `Idempotency Canvas ${RUN_ID}`,
    camera_code: `IDEMP-CAM-${RUN_ID}`,
    camera_name: `Idempotency Camera ${RUN_ID}`,
    idempotency_key: idempotency.canvas,
    updated_by: "warehouse-map-idempotency-smoke",
  });

  const secondDraft = await api("POST", "/api/admin/warehouse-map-drafts", {
    draft_name: `Idempotency smoke retry ${RUN_ID}`,
    grid: GRID,
    roles_base64: Buffer.from(roles).toString("base64"),
    created_by: "warehouse-map-idempotency-smoke",
  });
  const canvasRetry = await api("POST", `/api/admin/warehouse-map-drafts/${secondDraft.draft_id}/save-to-db`, {
    ware_id: WARE_ID,
    canvas_code: `IDEMP-CANVAS-${RUN_ID}-OTHER`,
    canvas_name: `Idempotency Canvas Retry ${RUN_ID}`,
    camera_code: `IDEMP-CAM-${RUN_ID}-OTHER`,
    camera_name: `Idempotency Camera Retry ${RUN_ID}`,
    idempotency_key: idempotency.canvas,
    updated_by: "warehouse-map-idempotency-smoke",
  });
  assertSame("canvas retry", canvas.canvas_id, canvasRetry.canvas_id);

  const topology = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/projection/save-to-topology`, {
    ware_id: WARE_ID,
    topology_code: `IDEMP-TOPO-${RUN_ID}`,
    topology_name: `Idempotency Topology ${RUN_ID}`,
    idempotency_key: idempotency.topology,
    updated_by: "warehouse-map-idempotency-smoke",
  });
  const topologyRetry = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/projection/save-to-topology`, {
    ware_id: WARE_ID,
    topology_code: `IDEMP-TOPO-${RUN_ID}-OTHER`,
    topology_name: `Idempotency Topology Retry ${RUN_ID}`,
    idempotency_key: idempotency.topology,
    updated_by: "warehouse-map-idempotency-smoke",
  });
  assertSame("topology retry", topology.topology_id, topologyRetry.topology_id);
  if (topologyRetry.idempotent !== true) {
    throw new Error("Topology retry did not report idempotent=true");
  }

  const routeDb = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/route/save-to-db`, {
    ware_id: WARE_ID,
    topology_id: topology.topology_id,
    route_code: `IDEMP-ROUTE-${RUN_ID}`,
    route_name: `Idempotency Route ${RUN_ID}`,
    route_pattern: "LINEAR",
    strict_sequence: 1,
    idempotency_key: idempotency.route,
    updated_by: "warehouse-map-idempotency-smoke",
  });
  const routeRetry = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/route/save-to-db`, {
    ware_id: WARE_ID,
    topology_id: topology.topology_id,
    route_code: `IDEMP-ROUTE-${RUN_ID}-OTHER`,
    route_name: `Idempotency Route Retry ${RUN_ID}`,
    route_pattern: "LINEAR",
    strict_sequence: 1,
    idempotency_key: idempotency.route,
    updated_by: "warehouse-map-idempotency-smoke",
  });
  assertSame("route retry", routeDb.pick_route_id, routeRetry.pick_route_id);
  if (routeRetry.idempotent !== true) {
    throw new Error("Route retry did not report idempotent=true");
  }

  const publish = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/publish-oracle`, {
    canvas_id: canvas.canvas_id,
    topology_id: topology.topology_id,
    pick_route_id: routeDb.pick_route_id,
    idempotency_key: idempotency.publish,
    published_by: "warehouse-map-idempotency-smoke",
  });
  const publishRetry = await api("POST", `/api/admin/warehouse-map-drafts/${draft.draft_id}/publish-oracle`, {
    canvas_id: canvas.canvas_id,
    topology_id: topology.topology_id,
    pick_route_id: routeDb.pick_route_id,
    idempotency_key: idempotency.publish,
    published_by: "warehouse-map-idempotency-smoke",
  });
  assertSame("publish retry canvas", publish.canvas_id, publishRetry.canvas_id);
  assertSame("publish retry topology", publish.topology_id, publishRetry.topology_id);
  assertSame("publish retry route", publish.pick_route_id, publishRetry.pick_route_id);
  if (publishRetry.idempotent !== true) {
    throw new Error("Publish retry did not report idempotent=true");
  }

  console.log(JSON.stringify({
    run_id: RUN_ID,
    ware_id: WARE_ID,
    canvas_id: canvas.canvas_id,
    topology_id: topology.topology_id,
    pick_route_id: routeDb.pick_route_id,
    idempotency,
    retry_flags: {
      topology: topologyRetry.idempotent === true,
      route: routeRetry.idempotent === true,
      publish: publishRetry.idempotent === true,
    },
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exit(1);
});
