const fs = require("node:fs");
const path = require("node:path");

const API_BASE = process.env.WMS_API_BASE || "http://127.0.0.1:8088";
const AUTH = "Basic " + Buffer.from(process.env.WMS_API_AUTH || "admin:admin123", "ascii").toString("base64");

function usage() {
  return [
    "Usage:",
    "  node tests/load/warehouse_map/warehouse_route_binding_loader.cjs --ware-id 1 --file bindings.json --dry-run",
    "  node tests/load/warehouse_map/warehouse_route_binding_loader.cjs --ware-id 1 --file bindings.csv --apply",
    "  node tests/load/warehouse_map/warehouse_route_binding_loader.cjs --file bindings.csv --validate-only",
    "",
    "JSON shape:",
    "  [{\"cell_code\":\"A1-001-L1\",\"articul\":\"SKU-1\"}]",
    "  {\"bindings\":[{\"pick_route_cell_id\":123,\"articul\":\"SKU-1\"}]}",
    "",
    "CSV header:",
    "  cell_code,articul,priority,min_qty,max_qty,case_pick_enabled,active",
  ].join("\n");
}

function parseArgs(argv) {
  const args = {
    wareId: Number(process.env.WMS_FIXTURE_WARE_ID || 1),
    file: null,
    dryRun: true,
    pickRouteId: null,
    limit: 5000,
    validateOnly: false,
  };
  for (let index = 2; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === "--help" || item === "-h") {
      console.log(usage());
      process.exit(0);
    }
    if (item === "--ware-id") args.wareId = Number(argv[++index]);
    else if (item === "--file") args.file = argv[++index];
    else if (item === "--apply") args.dryRun = false;
    else if (item === "--dry-run") args.dryRun = true;
    else if (item === "--validate-only") args.validateOnly = true;
    else if (item === "--pick-route-id") args.pickRouteId = Number(argv[++index]);
    else if (item === "--limit") args.limit = Number(argv[++index]);
    else throw new Error(`Unknown argument: ${item}\n${usage()}`);
  }
  if (!Number.isInteger(args.wareId) || args.wareId <= 0) {
    throw new Error("--ware-id must be a positive non-zero warehouse id.");
  }
  if (!args.file) {
    throw new Error(`--file is required.\n${usage()}`);
  }
  return args;
}

function parseCsv(text) {
  const lines = text.split(/\r?\n/).filter((line) => line.trim() && !line.trim().startsWith("#"));
  if (lines.length === 0) return [];
  const headers = splitCsvLine(lines[0]).map((header) => header.trim());
  return lines.slice(1).map((line) => {
    const values = splitCsvLine(line);
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] === undefined ? "" : values[index].trim();
    });
    return row;
  });
}

function splitCsvLine(line) {
  const values = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      value += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(value);
      value = "";
    } else {
      value += char;
    }
  }
  values.push(value);
  return values;
}

function loadBindings(filePath) {
  const absolute = path.resolve(filePath);
  const text = fs.readFileSync(absolute, "utf8");
  const ext = path.extname(absolute).toLowerCase();
  if (ext === ".json") {
    const parsed = JSON.parse(text);
    const rows = Array.isArray(parsed) ? parsed : parsed.bindings;
    if (!Array.isArray(rows)) {
      throw new Error("JSON binding file must be an array or an object with a bindings array.");
    }
    return rows;
  }
  if (ext === ".csv") return parseCsv(text);
  throw new Error("Binding file must be .json or .csv.");
}

function normalizeBinding(row, index) {
  const articul = String(row.articul || "").trim();
  if (!articul) throw new Error(`Binding row ${index + 1} has no articul.`);
  const pickRouteCellId = row.pick_route_cell_id === undefined || row.pick_route_cell_id === ""
    ? null
    : Number(row.pick_route_cell_id);
  if (pickRouteCellId !== null && (!Number.isInteger(pickRouteCellId) || pickRouteCellId <= 0)) {
    throw new Error(`Binding row ${index + 1} has invalid pick_route_cell_id.`);
  }
  const cellCode = row.cell_code === undefined || row.cell_code === null ? null : String(row.cell_code).trim();
  if (!pickRouteCellId && !cellCode) {
    throw new Error(`Binding row ${index + 1} must have pick_route_cell_id or cell_code.`);
  }
  return {
    pick_route_cell_id: pickRouteCellId,
    cell_code: cellCode || null,
    articul,
    priority: numberOrDefault(row.priority, 100),
    min_qty: nullableNumber(row.min_qty),
    max_qty: nullableNumber(row.max_qty),
    case_pick_enabled: intFlag(row.case_pick_enabled, 1),
    active: intFlag(row.active, 1),
  };
}

function nullableNumber(value) {
  if (value === undefined || value === null || value === "") return null;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`Invalid number: ${value}`);
  return parsed;
}

function numberOrDefault(value, fallback) {
  const parsed = nullableNumber(value);
  return parsed === null ? fallback : parsed;
}

function intFlag(value, fallback) {
  if (value === undefined || value === null || value === "") return fallback;
  const parsed = Number(value);
  if (parsed !== 0 && parsed !== 1) throw new Error(`Invalid flag: ${value}`);
  return parsed;
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

async function main() {
  const args = parseArgs(process.argv);
  const bindings = loadBindings(args.file).map(normalizeBinding);
  if (args.validateOnly) {
    console.log(JSON.stringify({
      valid: true,
      binding_count: bindings.length,
      dry_run: true,
      file: path.resolve(args.file),
    }, null, 2));
    return;
  }
  const result = await api("POST", `/api/picking/warehouses/${args.wareId}/route-consumption/materialize`, {
    pick_route_id: args.pickRouteId,
    create_missing_pick_faces: 1,
    bindings,
    dry_run: args.dryRun ? 1 : 0,
    limit: args.limit,
    updated_by: args.dryRun ? "route-binding-loader-dry-run" : "route-binding-loader",
  });
  console.log(JSON.stringify({
    ware_id: result.ware_id,
    dry_run: result.dry_run,
    route_cells_seen: result.route_cells_seen,
    created_pick_faces: result.created_pick_faces,
    existing_pick_faces: result.existing_pick_faces,
    skipped_without_pick_face: result.skipped_without_pick_face,
    assigned_articuls: result.assigned_articuls,
    readiness: result.readiness,
  }, null, 2));
  if (!args.dryRun) {
    console.log("Applied bindings. Re-run readiness before launching wave/case-pick.");
  }
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
