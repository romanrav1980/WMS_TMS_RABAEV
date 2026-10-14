// C-0034: время диаграммы Ганта. API отдаёт "YYYY-MM-DD HH:MM" без часового пояса (время БД) — пояс не пересчитывается.
// Интервал считается в минутах от 00:00 выбранной даты, поэтому рейс через полночь не теряет дату.
export type GanttTimed = { plan_start: string | null; plan_end: string | null };
export type DaySpan = { start: number; end: number };
export type ClippedSpan = DaySpan & { before: boolean; after: boolean };

export const DAY_MIN = 1440;
const STAMP = /^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})/;

// Локальная дата браузера (toISOString дала бы дату UTC — после полуночи по Москве это вчера).
export function localDayIso(d = new Date()): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function dayNumber(iso: string): number {
  const [y, m, d] = iso.split("-").map(Number);
  return Date.UTC(y, m - 1, d) / 86_400_000;
}

// Минуты от 00:00 дня `day`; без полной даты — null (неполные данные, а не «сегодня»).
export function stampMin(s: string | null | undefined, day: string): number | null {
  const m = s ? STAMP.exec(s) : null;
  if (!m) return null;
  const h = Number(m[2]), mi = Number(m[3]);
  if (h > 23 || mi > 59) return null;
  return (dayNumber(m[1]) - dayNumber(day)) * DAY_MIN + h * 60 + mi;
}

export function spanOf(op: GanttTimed, day: string): DaySpan | null {
  const start = stampMin(op.plan_start, day), end = stampMin(op.plan_end, day);
  if (start === null || end === null || end < start) return null;
  return { start, end };
}

// Сутки полуоткрытые [00:00, 24:00): начало в 24:00 и позже — уже следующие сутки; точка 00:00 — текущие.
// Обрезка по границам суток с признаками продолжения до/после; вне суток — null.
export function clipToDay(span: DaySpan): ClippedSpan | null {
  if (span.start >= DAY_MIN || span.end < 0 || (span.end === 0 && span.start < 0)) return null;
  return { start: Math.max(span.start, 0), end: Math.min(span.end, DAY_MIN), before: span.start < 0, after: span.end > DAY_MIN };
}

// "HH:MM" для выбранной даты, иначе "ДД.ММ HH:MM".
export function stampText(s: string | null | undefined, day: string): string {
  const m = s ? STAMP.exec(s) : null;
  if (!m) return s ? s : "—";
  return (m[1] === day ? "" : `${m[1].slice(8, 10)}.${m[1].slice(5, 7)} `) + `${m[2]}:${m[3]}`;
}

export const planText = (op: GanttTimed, day: string) => `${stampText(op.plan_start, day)} – ${stampText(op.plan_end, day)}`;

export type OffAxis<T> = { item: T; reason: "missing" | "outside" };
// Операции выборки, которых нет на шкале: без корректной даты или целиком вне выбранных суток.
export function offAxisOps<T extends GanttTimed>(ops: T[], day: string): OffAxis<T>[] {
  const out: OffAxis<T>[] = [];
  for (const op of ops) {
    const span = spanOf(op, day);
    if (!span) out.push({ item: op, reason: "missing" });
    else if (!clipToDay(span)) out.push({ item: op, reason: "outside" });
  }
  return out;
}

// Начальная прокрутка: сегодня — к текущему времени, иначе к первой операции суток, без операций — 06:00.
export function scrollTargetMin(day: string, ops: GanttTimed[], now = new Date()): number {
  if (day === localDayIso(now)) return now.getHours() * 60 + now.getMinutes();
  let first: number | null = null;
  for (const op of ops) {
    const span = spanOf(op, day), clip = span && clipToDay(span);
    if (clip && (first === null || clip.start < first)) first = clip.start;
  }
  return first ?? 360;
}

// Ближайшие операции после текущего момента (абсолютное время, а не HH:mm выбранной даты).
export function upcomingOps<T extends GanttTimed>(rows: { vehicle_num: string; operations: T[] }[], nowMin: number, limit = 5) {
  const today = localDayIso();
  const list: { vehicle_num: string; op: T; start: number }[] = [];
  for (const v of rows) for (const op of v.operations) {
    const start = stampMin(op.plan_start, today);
    if (start !== null && start > nowMin) list.push({ vehicle_num: v.vehicle_num, op, start });
  }
  return list.sort((a, b) => a.start - b.start).slice(0, limit);
}
