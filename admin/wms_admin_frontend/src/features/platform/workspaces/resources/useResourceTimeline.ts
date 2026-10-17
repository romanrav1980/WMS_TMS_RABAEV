import { useEffect, useState } from "react";
import { apiFetch } from "../../../../api";
import { ApiRequestError } from "../../../../api";
import { readError } from "../../access-admin";
import { TimelineShapeError, adaptTimeline } from "./timelineAdapter";
import type { ResourceTimeline } from "./timelineTypes";

const CODES: Record<number, string> = { 409: "В окне больше данных, чем разрешает предел сервера — сократите интервал (результат не обрезается молча).",
  422: "Интервал отклонён: нужен положительный интервал не длиннее 7 суток.", 503: "Источник ресурсов временно недоступен.", 404: "Склад не найден." };
function timelineError(reason: unknown): string {
  if (reason instanceof TimelineShapeError) return reason.message;
  if (reason instanceof ApiRequestError && CODES[reason.status]) {
    const code = typeof reason.detail === "object" && reason.detail && "code" in reason.detail ? ` (${String((reason.detail as { code: unknown }).code)})` : "";
    return CODES[reason.status] + code;
  }
  return readError(reason);
}

export const MAX_HOURS = 168; // черновой контракт C-0074: не больше 7 суток

/** Окно запроса в «настенном» времени склада: дата/час начала и длина. Браузерный пояс не используется. */
export type TimelineWindow = { warehouseId: string; startLocal: string; hours: number };

const pad = (n: number) => String(n).padStart(2, "0");
/** Настенное время склада → ISO с offset пояса склада (две итерации на случай перехода времени). */
export function wallToAware(wall: string, tz: string): string | null {
  const m = wall.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
  if (!m) return null;
  const target = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
  let guess = target;
  try {
    const f = new Intl.DateTimeFormat("en-CA", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
    for (let i = 0; i < 2; i++) {
      const p = Object.fromEntries(f.formatToParts(new Date(guess)).map(x => [x.type, x.value]));
      guess += target - Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute);
    }
  } catch { return null; }
  const off = Math.round((target - guess) / 60000), sign = off >= 0 ? "+" : "-";
  return `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:00${sign}${pad(Math.floor(Math.abs(off) / 60))}:${pad(Math.abs(off) % 60)}`;
}
export function addHoursWall(wall: string, hours: number): string {
  const d = new Date(Date.parse(wall.slice(0, 16) + ":00Z") + hours * 3600000);
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}T${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}`;
}

/** Путь запроса: сервер принимает только aware start_at/finish_at. При подтверждённом поясе склада окно задаётся во времени
 *  склада, иначе — в UTC с явной подписью (браузерный пояс не используется). Ночной интервал задаётся пересечением. */
export function timelinePath(w: TimelineWindow, tz: string | null): string | null {
  if (!w.warehouseId || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(w.startLocal)) return null;
  const hours = Math.max(1, Math.min(MAX_HOURS, w.hours)), finish = addHoursWall(w.startLocal, hours);
  const q = new URLSearchParams({ warehouse_id: w.warehouseId });
  const s = tz ? wallToAware(w.startLocal, tz) : null, f = tz ? wallToAware(finish, tz) : null;
  q.set("start_at", s ?? w.startLocal.slice(0, 16) + ":00+00:00"); q.set("finish_at", f ?? finish + ":00+00:00");
  return `/api/resources/timeline?${q.toString()}`;
}

export type TimelineRead = { data: ResourceTimeline | null; dataPath: string | null; path: string | null; error: string; loading: boolean; at: Date | null };

/** Чтение общего таймлайна ресурсов. Ответ хранится вместе со своим запросом: данные другого склада/окна не выдаются за текущие.
 *  Устаревший запрос отменяется; ошибка не превращается в пустой Гант. */
export function useResourceTimeline(w: TimelineWindow, tz: string | null, reload: number): TimelineRead {
  const path = timelinePath(w, tz);
  const [state, setState] = useState<Omit<TimelineRead, "path">>({ data: null, dataPath: null, error: "", loading: false, at: null });
  useEffect(() => {
    if (!path) { setState({ data: null, dataPath: null, error: "", loading: false, at: null }); return; }
    const controller = new AbortController();
    setState(old => ({ ...old, loading: true, error: "" }));
    apiFetch<unknown>(path, { signal: controller.signal })
      .then(raw => { const data = adaptTimeline(raw); if (!controller.signal.aborted) setState({ data, dataPath: path, error: "", loading: false, at: new Date() }); })
      .catch(reason => {
        if (controller.signal.aborted) return;
        // Отказ в доступе/вход/склад не найден: прежний ответ не показывается (право могли отозвать). Сеть/5xx — прежний ответ с пометкой.
        const denied = reason instanceof ApiRequestError && [401, 403, 404].includes(reason.status);
        setState(old => denied ? { data: null, dataPath: null, error: timelineError(reason), loading: false, at: null } : { ...old, loading: false, error: timelineError(reason) });
      });
    return () => controller.abort();
  }, [path, reload]);
  return { ...state, path };
}
