import { useEffect, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../api";

export type ReadState<T> = { data: T | null; error: string; loading: boolean; at: Date | null };

/** Чтение с отменой устаревшего запроса. Ошибка не превращается в пустые данные; null path — ничего не читать. */
export function useApiRead<T>(path: string | null, reload = 0): ReadState<T> {
  const [state, setState] = useState<ReadState<T> & { path: string | null }>({ path, data: null, error: "", loading: Boolean(path), at: null });
  useEffect(() => {
    if (!path) { setState({ path, data: null, error: "", loading: false, at: null }); return; }
    const controller = new AbortController();
    setState(old => old.path === path ? { ...old, loading: true, error: "" }
      : { path, data: null, error: "", loading: true, at: null });
    apiFetch<T>(path, { signal: controller.signal })
      .then(data => { if (!controller.signal.aborted) setState({ path, data, error: "", loading: false, at: new Date() }); })
      .catch(reason => {
        if (controller.signal.aborted) return;
        // 401/403/404 — прежние данные не показываются (право могли отозвать, объект исчез); сеть/5xx — прежние данные с ошибкой.
        const denied = reason instanceof ApiRequestError && [401, 403, 404].includes(reason.status);
        setState(old => denied || old.path !== path ? { path, data: null, error: readError(reason), loading: false, at: null }
          : { ...old, loading: false, error: readError(reason) });
      });
    return () => controller.abort();
  }, [path, reload]);
  return state.path === path ? state : { data: null, error: "", loading: Boolean(path), at: null };
}

export function readError(reason: unknown): string {
  if (reason instanceof ApiRequestError) {
    const detail = reason.detail as { code?: string; message?: string } | string;
    if (reason.status === 401) return "Сессия завершена — войдите снова.";
    if (reason.status === 403) return "Нет права просмотра" + (typeof detail === "object" && detail?.code ? ` (${detail.code})` : "") + ".";
    return `HTTP ${reason.status}: ${typeof detail === "string" ? detail : detail?.message ?? detail?.code ?? "ошибка"}`;
  }
  return "Сервер не ответил — данные не получены.";
}

/** datetime-local браузера → ISO8601 с явным смещением часового пояса (контракт требует timezone). */
export function localToOffsetIso(value: string): string {
  const date = new Date(value);
  const offset = -date.getTimezoneOffset();
  const sign = offset >= 0 ? "+" : "-";
  const pad = (n: number) => String(Math.floor(Math.abs(n))).padStart(2, "0");
  return `${value.length === 16 ? value + ":00" : value}${sign}${pad(offset / 60)}:${pad(offset % 60)}`;
}

export function formatMoment(value: string | null | undefined): string {
  if (!value) return "—";
  // Контракт требует часовой пояс. Значение без пояса не пересчитывается догадкой — показывается как есть с пометкой.
  if (!/(Z|[+-]\d{2}:?\d{2})$/.test(value)) return value.replace("T", " ").slice(0, 16) + " (без пояса)";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" });
}
