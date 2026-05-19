import { buildDemoEvents, buildDemoLayout, buildDemoMetrics, buildDemoReport } from "../demoData";
import type { MinuteMetrics, ReplayData, SimulationReport, WarehouseEvent, WarehouseLayout } from "../types";

const REPO_ROOT = "/@fs/C:/projects/TMS";

export async function loadReplayData(): Promise<ReplayData> {
  const params = new URLSearchParams(window.location.search);
  const hash = new URLSearchParams(window.location.hash.replace(/^#/, "").replace(/;/g, "&"));
  const runId = params.get("runId") || hash.get("runId");
  const evidenceDir = params.get("evidenceDir") || hash.get("evidenceDir")
    || (window as unknown as { WAREHOUSE_SIMULATION_EVIDENCE_DIR?: string }).WAREHOUSE_SIMULATION_EVIDENCE_DIR
    || (runId ? `runtime/test-evidence/warehouse-minute-simulation/${runId}` : "");

  if (!evidenceDir) return demoReplayData();

  try {
    const baseUrl = evidenceBaseUrl(evidenceDir);
    const [layout, eventsText, metricsText, report] = await Promise.all([
      fetchJson<WarehouseLayout>(`${baseUrl}/layout.json`),
      fetchText(`${baseUrl}/events.jsonl`),
      fetchTextOptional(`${baseUrl}/metrics-by-minute.csv`),
      fetchJsonOptional<SimulationReport>(`${baseUrl}/report.json`)
    ]);
    return {
      layout,
      events: parseJsonl(eventsText),
      metrics: metricsText ? parseCsv(metricsText) : [],
      report: report || {}
    };
  } catch (exc) {
    console.warn("Unable to load evidence, using demo fallback", exc);
    return demoReplayData();
  }
}

export function demoReplayData(): ReplayData {
  return {
    layout: buildDemoLayout(),
    events: buildDemoEvents(),
    metrics: buildDemoMetrics(),
    report: buildDemoReport()
  };
}

function evidenceBaseUrl(evidenceDir: string): string {
  if (/^https?:\/\//.test(evidenceDir) || evidenceDir.startsWith("/@fs/")) return evidenceDir.replace(/\/$/, "");
  const normalized = evidenceDir.replace(/\\/g, "/").replace(/^\.\.\//, "").replace(/^\.\//, "");
  if (normalized.startsWith("runtime/")) return `${REPO_ROOT}/${normalized}`;
  return normalized.replace(/\/$/, "");
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json() as Promise<T>;
}

async function fetchJsonOptional<T>(url: string): Promise<T | null> {
  try {
    return await fetchJson<T>(url);
  } catch {
    return null;
  }
}

async function fetchText(url: string): Promise<string> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.text();
}

async function fetchTextOptional(url: string): Promise<string> {
  try {
    return await fetchText(url);
  } catch {
    return "";
  }
}

export function parseJsonl(text: string): WarehouseEvent[] {
  return text.split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      const event = JSON.parse(line) as WarehouseEvent;
      return { ...event, id: event.id || `event-${index}`, minute: Number(event.minute || 0) };
    });
}

export function parseCsv(text: string): MinuteMetrics[] {
  const rows = text.split(/\r?\n/).filter(Boolean);
  if (!rows.length) return [];
  const headers = splitCsv(rows[0]);
  return rows.slice(1).map((row) => {
    const values = splitCsv(row);
    const parsed: Record<string, string | number> = {};
    headers.forEach((header, index) => {
      const value = values[index] ?? "";
      const numeric = Number(value);
      parsed[header] = value !== "" && Number.isFinite(numeric) ? numeric : value;
    });
    return parsed as MinuteMetrics;
  });
}

function splitCsv(line: string): string[] {
  const result: string[] = [];
  let value = "";
  let quoted = false;
  for (const char of line) {
    if (char === "\"") quoted = !quoted;
    else if (char === "," && !quoted) {
      result.push(value);
      value = "";
    } else {
      value += char;
    }
  }
  result.push(value);
  return result;
}
