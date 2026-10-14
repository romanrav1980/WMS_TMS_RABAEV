import type { Resource, St, StStage, Trip, TwinState } from "../contracts/twin";

export function clock(sec: number, withSeconds = false) {
  // Время суток: секунды могут выходить за текущие сутки (live-окна других дат), берём остаток по модулю суток.
  const total = ((Math.floor(sec) % 86400) + 86400) % 86400;
  const h = Math.floor(total / 3600) % 24;
  const m = Math.floor(total / 60) % 60;
  const s = total % 60;
  const base = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
  return withSeconds ? `${base}:${String(s).padStart(2, "0")}` : base;
}

export const fmt = (n: number) => n.toLocaleString("ru-RU");

export const STAGE_LABEL: Record<StStage, string> = {
  created: "Создано",
  picking: "Отбор",
  picked: "Собрано",
  qc: "Контроль",
  staged: "У ворот",
  loading: "Погрузка",
  loaded: "Загружено",
  shipped: "В пути",
  delivered: "Доставлено"
};

export type Tone = "ok" | "info" | "warn" | "crit" | "idle";

export function tripStatus(trip: Trip): { label: string; tone: Tone } {
  if (trip.conditionRaw !== undefined && (trip.phase === "planned" || trip.phase === "done")) {
    return { label: trip.conditionRaw || "—", tone: trip.phase === "done" ? "idle" : "info" };
  }
  switch (trip.phase) {
    case "planned":
      return { label: "Запланирован", tone: "idle" };
    case "arriving":
      return { label: trip.queueSlot >= 0 ? "Въезд · к очереди" : "Въезд", tone: "info" };
    case "queued":
      return { label: "Очередь к воротам", tone: "warn" };
    case "reversing":
      return { label: "Постановка задним ходом", tone: "info" };
    case "docked":
      if (trip.waitReason?.startsWith("Ждёт")) return { label: "Ждёт СТ", tone: "warn" };
      return { label: trip.direction === "out" ? "Погрузка" : "Выгрузка", tone: "ok" };
    case "departing":
      return { label: "Выезд", tone: "info" };
    case "transit":
      return { label: "В пути к магазинам", tone: "info" };
    case "done":
      return { label: trip.direction === "out" ? "Доставлен" : "Закрыт", tone: "idle" };
  }
}

export function riskBadge(trip: Trip): { label: string; tone: Tone } | undefined {
  if (trip.risk === "late") return { label: "Опоздание", tone: "crit" };
  if (trip.risk === "risk") return { label: "Риск окна", tone: "warn" };
  return undefined;
}

export function resourceStatus(r: Resource, w: TwinState): { label: string; tone: Tone } {
  if (r.status === "charging") return { label: `Зарядка ${Math.round(r.battery)}%`, tone: "idle" };
  if (r.status === "waiting") return { label: "Ожидание", tone: "crit" };
  if (r.leg === "toCharger") return { label: "На зарядку", tone: "warn" };
  if (r.kind === "picker") {
    if (r.stId) return { label: r.leg === "toStaging" ? "К воротам" : r.status === "working" ? "Отбор" : "К ячейке", tone: r.status === "working" ? "ok" : "info" };
    return { label: "Свободен", tone: "idle" };
  }
  const task = w.tasks.find((t) => t.id === r.taskId);
  if (!task) return { label: "Ждёт задание", tone: "idle" };
  const verb = { REPL: "Пополнение", PUTAWAY: "Размещение", LOAD: "Погрузка", UNLOAD: "Выгрузка" }[task.kind];
  return { label: verb, tone: r.status === "working" ? "ok" : "info" };
}

export function stProgress(st: St) {
  const picked = st.lines.filter((l) => l.picked).length;
  return { picked, total: st.lines.length };
}

// Дата и время отгрузки из ТМС (ISO без зоны — локальное время сервера).
export function shipmentLabel(iso?: string) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const date = d.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
  const time = d.getHours() || d.getMinutes() ? ` ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}` : "";
  return `${date}${time}`;
}

export function minutesAgo(now: number, at?: number) {
  if (at === undefined) return "—";
  const m = Math.max(0, Math.round((now - at) / 60));
  return m === 0 ? "только что" : `${m} мин назад`;
}
