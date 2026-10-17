import type { Availability, ResourceTimeline, ResourceType, TimelineBinding, TimelineEvent, TimelineResource } from "./timelineTypes";

// Чистая модель общего Ганта. Ось — «настенные» минуты склада при подтверждённом поясе, иначе UTC (с подписью).
// На ось попадают только aware-моменты; старое время без offset — никогда (очередь «без пояса»), даже при известном поясе.
// «Сейчас» — реальный момент чтения; местные опоздания РЦ без пояса не рассчитываются. Браузерный пояс не используется.

const OFFSET = /(Z|[+-]\d{2}:?\d{2})$/;
export const isAware = (iso: string) => OFFSET.test(iso.trim());

function literalMinutes(iso: string): number | null {
  const m = iso.trim().match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?/);
  if (!m) return null;
  return Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)) / 60000;
}
const partsCache = new Map<string, Intl.DateTimeFormat>();
function zoneMinutes(instant: Date, tz: string): number | null {
  let f = partsCache.get(tz);
  try {
    if (!f) { f = new Intl.DateTimeFormat("en-CA", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" }); partsCache.set(tz, f); }
  } catch { return null; }
  const p = Object.fromEntries(f.formatToParts(instant).map(x => [x.type, x.value]));
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) / 60000;
}
/** Минуты оси для строки времени API. null — время не задано, не разобрано или без пояса при неподтверждённом поясе склада. */
export function axisMinutes(iso: string | null | undefined, tz: string | null): number | null {
  if (!iso) return null;
  if (isAware(iso)) { const d = new Date(iso); if (Number.isNaN(d.getTime())) return null; return tz ? zoneMinutes(d, tz) : Math.floor(d.getTime() / 60000); }
  return null; // время без offset (старое местное) на общую ось не ставится (C-0075/C-0078)
}
const hasTime = (iso: string | null | undefined) => Boolean(iso && literalMinutes(iso) != null);
export const zoneKnown = (t: ResourceTimeline) => { if (!t.warehouse.time_zone) return false; try { new Intl.DateTimeFormat("ru", { timeZone: t.warehouse.time_zone }); return true; } catch { return false; } };
/** «Сейчас» — момент чтения сервера (aware) на той же оси. Без aware момента линии нет. */
export const nowAxis = (t: ResourceTimeline) => axisMinutes(t.read_at, zoneKnown(t) ? t.warehouse.time_zone : null);

export const fmtAxis = (min: number, withDate = false) => {
  const d = new Date(min * 60000), hh = String(d.getUTCHours()).padStart(2, "0"), mm = String(d.getUTCMinutes()).padStart(2, "0");
  return withDate ? `${String(d.getUTCDate()).padStart(2, "0")}.${String(d.getUTCMonth() + 1).padStart(2, "0")} ${hh}:${mm}` : `${hh}:${mm}`;
};

/** Время для карточки: в поясе склада; без подтверждённого пояса — цифры источника с явной пометкой, без пересчёта браузером. */
export function fmtTime(tz: string | null, iso: string | null | undefined): string {
  if (!iso) return "—";
  const m = axisMinutes(iso, tz);
  if (m == null) return iso.replace("T", " ").slice(0, 16) + " (без пояса)";
  return fmtAxis(m, true) + (tz ? "" : " UTC");
}

export type Bar = { key: string; event: TimelineEvent; binding: TimelineBinding; basis: "PLAN" | "FACT";
  start: number; end: number; open: boolean; point: boolean; conflict: boolean };
export type Segment = { start: number; end: number; open: boolean; a: Availability };
export type Row = { resource: TimelineResource; bars: Bar[]; availability: Segment[]; conflicts: number; sourceDown: boolean };

function barOf(b: TimelineBinding, e: TimelineEvent, tz: string | null, readAt: number | null): Bar | null {
  const fact = b.basis === "FACT";
  const s = axisMinutes(b.start_at ?? (fact ? e.fact_start_at : e.plan_start_at), tz);
  if (s == null) return null;
  const f = axisMinutes(b.finish_at ?? (fact ? e.fact_finish_at : e.plan_finish_at), tz);
  // Незавершённый факт тянется только до момента чтения (подтверждено, что ещё идёт), окончание не выдумывается.
  // Терминальный статус без окончания (сборка закрыта, finish у источника не известен) — точка, не заливка до «сейчас».
  if (f == null && fact && !e.terminal && readAt != null && readAt >= s) return { key: b.binding_id, event: e, binding: b, basis: b.basis, start: s, end: readAt, open: true, point: false, conflict: false };
  if (f == null || f < s) return { key: b.binding_id, event: e, binding: b, basis: b.basis, start: s, end: s, open: true, point: true, conflict: false };
  return { key: b.binding_id, event: e, binding: b, basis: b.basis, start: s, end: f, open: false, point: false, conflict: false };
}

/** Пересечение подтверждённых интервалов одного ресурса разными event_id в одном основании (план с планом, факт с фактом).
 *  Это основание для проверки, не запрет параллельной работы: правила ресурса в контракте нет. */
export function markConflicts(bars: Bar[], server?: { basis: "PLAN" | "FACT"; event_ids: string[] }[]): number {
  let n = 0;
  if (server) { // кандидаты сервера — источник истины; браузер не пересчитывает
    for (const b of bars) b.conflict = server.some(o => o.basis === b.basis && o.event_ids.includes(b.event.event_id));
    return bars.filter(b => b.conflict).length;
  }
  for (const basis of ["PLAN", "FACT"] as const) {
    const list = bars.filter(b => b.basis === basis && !b.point).sort((a, b) => a.start - b.start);
    for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length && list[j].start < list[i].end; j++) {
      if (list[j].event.event_id === list[i].event.event_id) continue;
      if (!list[i].conflict) n++; if (!list[j].conflict) n++;
      list[i].conflict = list[j].conflict = true;
    }
  }
  return n;
}

/** waveId/waveLabel — структурный фильтр по точному числовому wave_id события (не по тексту wave_code, его в hay текстового
 *  поиска нет — C-0110). Независим от query: ручной поиск не трогает и не трогается этим фильтром. */
export type Filters = { types: Set<ResourceType>; query: string; groupBy: "type" | "warehouse"; onlyConflicts: boolean; waveId: number | null; waveLabel: string | null };
export type Group = { key: string; label: string; rows: Row[] };

function matches(r: TimelineResource, bars: Bar[], q: string) {
  if (!q) return true;
  const hay = [r.code, r.name, r.zone_code, r.warehouse_name, String(r.warehouse_id), ...bars.flatMap(b => [b.event.title, b.event.event_id, b.event.wave_id, b.event.task_id, b.event.trip_id])];
  return hay.some(v => v != null && String(v).toLowerCase().includes(q));
}
const hasWave = (bars: Bar[], waveId: number) => bars.some(b => b.event.wave_id === waveId);

export function buildRows(t: ResourceTimeline): Row[] {
  const tz = zoneKnown(t) ? t.warehouse.time_zone : null, readAt = axisMinutes(t.read_at, tz);
  const events = new Map(t.events.map(e => [e.event_id, e]));
  const down = new Set(t.sources.filter(s => s.status !== "OK").map(s => s.source));
  const byRes = new Map<string, TimelineBinding[]>();
  for (const b of t.bindings) (byRes.get(b.resource_key) ?? byRes.set(b.resource_key, []).get(b.resource_key)!).push(b);
  return t.resources.map(resource => {
    const bars = (byRes.get(resource.resource_key) ?? []).flatMap(b => { const e = events.get(b.event_id); const bar = e && barOf(b, e, tz, readAt); return bar ? [bar] : []; });
    const availability = resource.availability.flatMap(a => {
      const s = axisMinutes(a.start_at, tz); if (s == null) return [];
      const f = axisMinutes(a.finish_at, tz);
      return [{ start: s, end: f ?? s, open: f == null, a }];
    });
    const conflicts = markConflicts(bars, t.overlaps?.filter(o => o.resource_key === resource.resource_key));
    const sourceDown = resource.availability.some(a => down.has(a.source)) || bars.some(b => down.has(b.event.source));
    return { resource, bars, availability, conflicts, sourceDown };
  });
}

export function groupRows(rows: Row[], f: Filters, typeLabel: (t: ResourceType) => string): Group[] {
  const q = f.query.trim().toLowerCase();
  const list = rows.filter(r => f.types.has(r.resource.resource_type) && matches(r.resource, r.bars, q) && (!f.onlyConflicts || r.conflicts > 0)
    && (f.waveId == null || hasWave(r.bars, f.waveId)));
  const groups = new Map<string, Group>();
  for (const r of list) {
    const key = f.groupBy === "type" ? r.resource.resource_type : `${r.resource.warehouse_id}`;
    const label = f.groupBy === "type" ? typeLabel(r.resource.resource_type) : (r.resource.warehouse_name || `Склад ${r.resource.warehouse_id}`);
    (groups.get(key) ?? groups.set(key, { key, label, rows: [] }).get(key)!).rows.push(r);
  }
  return [...groups.values()];
}

/** Работы без времени или без ресурса — отдельная очередь, длительность не выдумывается. */
export type QueueItem = { event: TimelineEvent; reason: "NO_TIME" | "NO_RESOURCE" | "NO_ZONE" };
export function unscheduled(t: ResourceTimeline): QueueItem[] {
  const tz = zoneKnown(t) ? t.warehouse.time_zone : null;
  const bound = new Map<string, TimelineBinding[]>();
  for (const b of t.bindings) (bound.get(b.event_id) ?? bound.set(b.event_id, []).get(b.event_id)!).push(b);
  return t.events.flatMap((e): QueueItem[] => {
    const bs = bound.get(e.event_id) ?? [];
    const starts = bs.length ? bs.map(b => b.start_at ?? (b.basis === "FACT" ? e.fact_start_at : e.plan_start_at)) : [e.plan_start_at, e.fact_start_at];
    if (starts.some(x => axisMinutes(x, tz) != null)) return bs.length ? [] : [{ event: e, reason: "NO_RESOURCE" }];
    const legacy = Object.values(e.legacy_time ?? {}).some(Boolean) || starts.some(hasTime);
    return [{ event: e, reason: legacy ? "NO_ZONE" : bs.length ? "NO_TIME" : "NO_RESOURCE" }];
  });
}

/** Сводка без удвоения: события считаются по event_id, объёмы разных товаров не складываются: API не даёт ключ SKU для такого итога. */
export function summarize(t: ResourceTimeline, rows: Row[]) {
  const ids = new Set(rows.flatMap(r => r.bars.map(b => b.event.event_id)));
  const quantifiedEvents = new Set(t.events.filter(e => ids.has(e.event_id) && e.quantity != null).map(e => e.event_id)).size;
  return { events: ids.size, resources: rows.length, conflicts: rows.reduce((n, r) => n + r.conflicts, 0), bindings: rows.reduce((n, r) => n + r.bars.length, 0), quantifiedEvents };
}

export type NowState = { label: string; tone: "busy" | "free" | "plan" | "off" | "down" | "unknown"; basis: string };
/** Состояние ресурса «сейчас». Свободным считается только при подтверждённой смене, известном поясе, рабочем источнике и без открытого факта. */
export function stateNow(row: Row, now: number | null): NowState {
  const open = row.bars.find(b => b.basis === "FACT" && b.open && !b.point);
  if (open) return { label: "Занят (факт идёт)", tone: "busy", basis: `${open.event.title} · факт с ${fmtAxis(open.start)}` };
  if (now == null) return { label: "Неизвестно", tone: "unknown", basis: "Нет момента чтения сервера — состояние на текущий момент не рассчитывается" };
  if (row.resource.source_state === "BLOCKED") return { label: "Заблокирован", tone: "down", basis: "Состояние в реестре источника: BLOCKED" };
  if (row.sourceDown) return { label: "Неизвестно", tone: "unknown", basis: "Источник доступности или занятости не ответил" };
  const seg = row.availability.find(s => s.start <= now && (s.open || s.end > now));
  if (!seg || seg.a.state === "UNKNOWN") return { label: "Неизвестно", tone: "unknown", basis: "Нет подтверждённых данных о смене/доступности" };
  if (seg.a.state === "OFF_SHIFT") return { label: "Не на смене", tone: "off", basis: seg.a.reason || seg.a.source };
  if (seg.a.state === "DOWN") return { label: "Недоступен", tone: "down", basis: seg.a.reason || seg.a.source };
  const planned = seg.a.state === "PLANNED";
  const busy = row.bars.find(b => !b.point && b.start <= now && b.end > now);
  if (busy) return { label: busy.basis === "FACT" ? "Занят (факт)" : "Занят по плану", tone: "busy", basis: busy.event.title };
  // План выхода — не подтверждённое присутствие: «без назначений по плану», а не «свободен».
  if (planned) return { label: "Без назначений (план выхода)", tone: "plan", basis: `План выхода по ${seg.a.source}; фактическое присутствие источником не подтверждено` };
  return { label: "Свободен", tone: "free", basis: `На смене по ${seg.a.source}, назначений на текущий момент нет` };
}

/** Видимое окно оси. Шаг делений подбирается по ширине окна. */
export function ticks(from: number, to: number): number[] {
  const span = to - from, step = span <= 240 ? 30 : span <= 720 ? 60 : span <= 1440 ? 120 : span <= 4320 ? 360 : 720;
  const out: number[] = []; for (let m = Math.ceil(from / step) * step; m <= to; m += step) out.push(m);
  return out;
}
