import type { MinuteMetrics, SimulationReport, WarehouseEvent, WarehouseLayout } from "./types";

export const SHIFT_MINUTES = 720;

export function clock(minute: number): string {
  const value = 8 * 60 + minute;
  return `${String(Math.floor(value / 60)).padStart(2, "0")}:${String(value % 60).padStart(2, "0")}`;
}

export function buildDemoLayout(): WarehouseLayout {
  const cells = [];
  const gates = [];
  for (let aisle = 1; aisle <= 25; aisle += 1) {
    const y = (aisle - 1) * 4;
    gates.push({ gate_id: `G${String(aisle).padStart(2, "0")}`, aisle, x_m: 0, y_m: y });
    for (let slot = 1; slot <= 60; slot += 1) {
      const role = slot % 13 === 0 ? "DYNAMIC_PICK_FACE" : slot % 17 === 0 ? "DUPLICATE_A_PICK_FACE" : "FIXED_PICK_FACE";
      cells.push({
        cell_id: `A${String(aisle).padStart(2, "0")}-S${String(slot).padStart(3, "0")}-L1`,
        aisle,
        slot,
        level: 1,
        x_m: (slot - 1) * 1.5,
        y_m: y,
        role
      });
    }
  }
  return { run_id: "demo-react", cells, gates };
}

export function buildDemoEvents(): WarehouseEvent[] {
  const events: WarehouseEvent[] = [];
  for (let wave = 1; wave <= 10; wave += 1) {
    const minute = (wave - 1) * 60;
    events.push({ minute, clock: clock(minute), event_type: "WAVE_LAUNCHED", wave_id: `WAVE-SIM-${String(wave).padStart(2, "0")}` });
  }
  for (let minute = 6; minute <= SHIFT_MINUTES; minute += 8) {
    const waveId = inferWaveByMinute(minute);
    const aisle = 1 + (minute % 25);
    const slot = 1 + (minute % 60);
    events.push({
      minute,
      clock: clock(minute),
      event_type: "PICKER_TASK_STARTED",
      resource_id: `P${String((minute % 10) + 1).padStart(2, "0")}`,
      wave_id: waveId,
      client_id: `C${String(Math.min(50, Math.ceil(minute / 12))).padStart(3, "0")}`,
      pallet_id: `CP-${minute}`,
      sku_id: `SKU-${String((minute % 1000) + 1).padStart(4, "0")}`,
      cell: `A${String(aisle).padStart(2, "0")}-S${String(slot).padStart(3, "0")}-L1`
    });
  }
  for (let minute = 8; minute <= SHIFT_MINUTES; minute += 13) {
    const waveId = inferWaveByMinute(minute);
    const source = `A${String(1 + (minute % 25)).padStart(2, "0")}-S${String(20 + (minute % 30)).padStart(3, "0")}-L1`;
    const target = `A${String(1 + ((minute + 3) % 25)).padStart(2, "0")}-S${String(1 + (minute % 45)).padStart(3, "0")}-L1`;
    const rt = `RT${String((minute % 5) + 1).padStart(2, "0")}`;
    events.push({ minute, clock: clock(minute), event_type: "REPLENISHMENT_RELEASED", task_id: `RPL-${minute}`, resource_id: rt, wave_id: waveId, sku_id: `SKU-${String((minute % 1000) + 1).padStart(4, "0")}`, source_cell: source, target_cell: target });
    events.push({ minute: minute + 1, clock: clock(minute + 1), event_type: "REACHTRUCK_TASK_STARTED", task_id: `RPL-${minute}`, resource_id: rt, wave_id: waveId, source_cell: source, target_cell: target });
    events.push({ minute: minute + 7, clock: clock(minute + 7), event_type: "REPLENISHMENT_DONE", task_id: `RPL-${minute}`, resource_id: rt, wave_id: waveId, source_cell: source, target_cell: target });
  }
  ([
    "PICK_FACE_EMPTY",
    "PICK_FACE_QUEUE",
    "AISLE_CONGESTION",
    "REACHTRUCK_BLOCK",
    "REACHTRUCK_CROSSING",
    "REACHTRUCK_PICKER_PASS",
    "ROUTE_COMPLETION_DELAY",
    "PALLET_TO_DOCK_DELAY",
    "DOCK_QUEUE",
    "REACH_RESOURCE_SHORTAGE"
  ] as const).forEach((type, offset) => {
    for (let minute = 42 + offset * 17; minute <= 690; minute += 91) {
      const aisle = 1 + ((minute + offset) % 25);
      const slot = 1 + (minute % 55);
      events.push({
        minute,
        clock: clock(minute),
        event_type: "COLLISION",
        collision_type: type,
        wave_id: inferWaveByMinute(minute),
        cell: `A${String(aisle).padStart(2, "0")}-S${String(slot).padStart(3, "0")}-L1`,
        resources: [`P${String((minute % 10) + 1).padStart(2, "0")}`, `RT${String((minute % 5) + 1).padStart(2, "0")}`],
        lost_minutes: 4 + (minute % 8)
      });
    }
  });
  return events.sort((a, b) => a.minute - b.minute);
}

export function buildDemoMetrics(): MinuteMetrics[] {
  return Array.from({ length: SHIFT_MINUTES + 1 }, (_, minute) => ({
    minute,
    done_pick_lines: Math.round(minute * 13.1),
    total_pick_lines: 9447,
    picker_busy: Math.min(10, Math.ceil(minute / 18))
  }));
}

export function buildDemoReport(): SimulationReport {
  return {
    run_id: "demo-react",
    scenario: { clients: 50, waves: 10, sku: 1000, pick_faces: 1500, pickers: 10, reachtrucks: 5 },
    totals: { pick_lines: 9447, replenishment_tasks: 90, shipped_pallets: 202, collisions: 121, lost_minutes: 247 }
  };
}

export function inferWaveByMinute(minute: number): string {
  return `WAVE-SIM-${String(Math.min(10, Math.floor(minute / 60) + 1)).padStart(2, "0")}`;
}
