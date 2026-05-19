import fs from "node:fs";
import path from "node:path";

const evidenceDir = process.argv[2];

if (!evidenceDir) {
  console.error("Usage: node tests/load/wave/warehouse_simulation_ui_contract_check.mjs <evidence-dir>");
  process.exit(2);
}

const layout = readJson("layout.json");
const events = readJsonl("events.jsonl");
const metrics = readCsv("metrics-by-minute.csv");
const collisions = readCsv("collision-report.csv");
const report = readJson("report.json");

assert(Array.isArray(layout.cells) && layout.cells.length >= 1500, "layout.cells must contain the warehouse cells");
assert(Array.isArray(layout.gates) && layout.gates.length >= 25, "layout.gates must contain G01..G25");
assert(events.length > 0, "events.jsonl must contain replay events");
assert(events.every((event) => Number.isFinite(Number(event.minute))), "every event must have numeric minute");
assert(events.some((event) => event.event_type === "WAVE_LAUNCHED"), "events must include wave launch markers");
assert(events.some((event) => event.event_type === "COLLISION"), "events must include collision markers");
assert(metrics.length > 0, "metrics-by-minute.csv must not be empty");
assert(collisions.length > 0, "collision-report.csv must not be empty");
assert(report.run_id, "report.json must contain run_id");

const replayState = reduceReplayState(events, 180);
assert(Object.keys(replayState.resources).length > 0, "replay reducer must reconstruct resource state");
assert(replayState.activeCollisions.length > 0, "replay reducer must expose active/recent collisions");

console.log(JSON.stringify({
  ok: true,
  cells: layout.cells.length,
  gates: layout.gates.length,
  events: events.length,
  metrics: metrics.length,
  collisions: collisions.length,
  resourcesAt180: Object.keys(replayState.resources).length,
  activeCollisionsAt180: replayState.activeCollisions.length,
}, null, 2));

function readJson(name) {
  return JSON.parse(fs.readFileSync(path.join(evidenceDir, name), "utf8"));
}

function readJsonl(name) {
  return fs.readFileSync(path.join(evidenceDir, name), "utf8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function readCsv(name) {
  const rows = fs.readFileSync(path.join(evidenceDir, name), "utf8")
    .split(/\r?\n/)
    .filter(Boolean);
  if (!rows.length) return [];
  const headers = rows[0].split(",");
  return rows.slice(1).map((row) => {
    const values = row.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function reduceReplayState(events, minute) {
  const resources = {};
  const activeCollisions = [];
  for (const event of events) {
    if (Number(event.minute) > minute) continue;
    if (event.resource_id) {
      resources[event.resource_id] = {
        resourceId: event.resource_id,
        waveId: event.wave_id,
        taskId: event.task_id,
        sku: event.sku_id,
        locationId: event.cell || event.target_cell || event.source_cell,
        lastEventType: event.event_type,
        lastMinute: Number(event.minute),
      };
    }
    if (event.event_type === "COLLISION" && Number(event.minute) >= minute - 120) {
      activeCollisions.push(event);
    }
  }
  return { resources, activeCollisions };
}

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}
