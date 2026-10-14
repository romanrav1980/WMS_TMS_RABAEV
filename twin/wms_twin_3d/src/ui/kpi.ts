import type { TwinState } from "../contracts/twin";

// Агрегаты для HUD считаются из того же TwinState, что и сцена, — панели и 3D не расходятся.
export function computeKpi(w: TwinState) {
  const sts = Object.values(w.sts);
  const trips = w.trips;
  const onSite = trips.filter((t) => ["arriving", "queued", "reversing", "docked", "departing"].includes(t.phase));
  const docked = trips.filter((t) => t.dockedAt !== undefined);
  const onTime = docked.filter((t) => t.onTime).length;
  const faces = w.cells.filter((c) => c.role === "pick" && c.stockKnown !== false);
  const reserve = w.cells.filter((c) => c.role === "reserve" && c.stockKnown !== false);
  const active = w.collisions.filter((c) => c.active);
  return {
    linesPerHour: w.counters.pickTimes.length,
    linesPicked: w.counters.linesPicked,
    stInWork: sts.filter((s) => ["created", "picking", "picked", "qc", "staged", "loading"].includes(s.stage)).length,
    stShipped: sts.filter((s) => s.stage === "shipped" || s.stage === "delivered").length,
    trucksOnSite: onSite.length,
    trucksQueued: trips.filter((t) => t.phase === "queued").length,
    trucksTransit: trips.filter((t) => t.phase === "transit").length,
    onTimePct: docked.length ? (onTime / docked.length) * 100 : 100,
    dockedCount: docked.length,
    lateCount: docked.length - onTime,
    gatesBusy: w.gates.filter((g) => g.occupiedBy).length,
    gatesTotal: w.gates.length,
    reserveFill: reserve.length ? reserve.filter((c) => c.qty > 0).length / reserve.length : 0,
    facesEmpty: faces.filter((c) => c.qty === 0).length,
    facesLow: faces.filter((c) => c.qty > 0 && c.qty <= 10).length,
    replQueue: w.tasks.filter((t) => (t.kind === "REPL" || t.kind === "PUTAWAY") && t.status !== "done").length,
    replSla: w.counters.replDone ? (w.counters.replOnTime / w.counters.replDone) * 100 : 100,
    palletsReceived: w.counters.palletsReceived,
    palletsShipped: w.counters.palletsShipped,
    collisionsActive: active.length,
    collisionsCritical: active.filter((c) => c.severity === "critical").length,
    lostMinutes: w.collisions.reduce((sum, c) => sum + c.lostMinutes, 0)
  };
}

export type Kpi = ReturnType<typeof computeKpi>;

// Шаги процесса площадки для левой панели «Поток площадки».
export function computeFlow(w: TwinState) {
  const sts = Object.values(w.sts);
  const count = (stages: string[]) => sts.filter((s) => stages.includes(s.stage)).length;
  const trips = w.trips;
  const pickers = w.resources.filter((r) => r.kind === "picker");
  const reach = w.resources.filter((r) => r.kind === "reachtruck");
  const fork = w.resources.filter((r) => r.kind === "forklift");
  const tasks = (kind: string) => w.tasks.filter((t) => t.kind === kind && t.status !== "done").length;
  return [
    { key: "yard", icon: "⛟", title: "Въезд · двор", value: trips.filter((t) => ["arriving", "queued", "reversing"].includes(t.phase)).length, note: `${trips.filter((t) => t.phase === "queued").length} в очереди к воротам` },
    { key: "inbound", icon: "⇩", title: "Приёмка", value: trips.filter((t) => t.direction === "in" && t.phase === "docked").length, note: `${w.counters.palletsReceived} палл. размещено · выгрузка ${tasks("UNLOAD")}` },
    { key: "putaway", icon: "▤", title: "Размещение · пополнение", value: tasks("PUTAWAY") + tasks("REPL"), note: `Ричтраки ${reach.filter((r) => r.taskId).length}/${reach.length} заняты` },
    { key: "picking", icon: "✋", title: "Отбор волны", value: count(["picking"]), note: `${count(["created"])} СТ ждут · комплект. ${pickers.filter((r) => r.stId).length}/${pickers.length}` },
    { key: "qc", icon: "✓", title: "Контроль", value: count(["picked", "qc"]), note: "весовой и составной контроль СТ" },
    { key: "staging", icon: "▦", title: "Выставка к воротам", value: count(["staged", "loading"]), note: "СТ у ворот своего рейса" },
    { key: "loading", icon: "⇧", title: "Погрузка рейса", value: trips.filter((t) => t.direction === "out" && t.phase === "docked").length, note: `Погрузчики ${fork.filter((r) => r.taskId).length}/${fork.length} · ворота ${w.gates.filter((g) => g.occupiedBy).length}/${w.gates.length}` },
    { key: "transit", icon: "➜", title: "Рейсы в пути", value: trips.filter((t) => t.phase === "transit").length, note: `${count(["delivered"])} СТ доставлено` }
  ];
}
