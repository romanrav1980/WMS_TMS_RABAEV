// C-0172: пояс исходных местных значений рейса (окна СТ, операции). Расчёт окон трактует их в переданном time_zone
// (native from_tz), поэтому пояс берётся только из подтверждённых данных рейса, а не выбирается для показа.
export type Zone = "Europe/Moscow" | "Asia/Tbilisi" | "UTC";
export type ZoneSource = { zone: Zone | null; basis: "APPROVAL" | null; reason: "MIXED_ZONES" | "UNCONFIRMED" | null; zones: string[] };
type TimeContext = { last_approval?: { time_zone?: string | null } | null;
  source?: { store_window_profiles?: { time_zone?: string | null; profile_absent?: boolean }[] } | null };

const KNOWN: readonly string[] = ["Europe/Moscow", "Asia/Tbilisi", "UTC"];

/** Основание пояса исходных значений — только явный пояс утверждения времени рейса. Пояса карточек магазинов его не доказывают;
 *  магазины в другом поясе — ограничение текущего расчёта (один пояс на рейс), а не ошибка карточек. */
export function sourceZone(context: TimeContext | null | undefined): ZoneSource {
  const stores = [...new Set((context?.source?.store_window_profiles ?? []).filter(p => !p.profile_absent && p.time_zone).map(p => String(p.time_zone)))];
  const approved = context?.last_approval?.time_zone ?? null;
  if (!approved || !KNOWN.includes(approved)) return { zone: null, basis: null, reason: "UNCONFIRMED", zones: stores };
  if (stores.some(z => z !== approved)) return { zone: null, basis: null, reason: "MIXED_ZONES", zones: [approved, ...stores.filter(z => z !== approved)] };
  return { zone: approved as Zone, basis: "APPROVAL", reason: null, zones: [approved] };
}

/** Момент со своим смещением из ответа: «29.10 12:48 (UTC+03:00)». Один и тот же момент не переобозначается. */
export function stamp(iso: string | null | undefined): string {
  if (!iso) return "неизвестно";
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}).*?(Z|[+-]\d{2}:\d{2})$/.exec(iso);
  if (!m) return "неизвестно";
  return `${m[3]}.${m[2]} ${m[4]}:${m[5]} (UTC${m[6] === "Z" || m[6] === "+00:00" ? "" : m[6]})`;
}

export function minutesBetween(from: string, to: string): number {
  return Math.ceil((Date.parse(to) - Date.parse(from)) / 60000);
}
