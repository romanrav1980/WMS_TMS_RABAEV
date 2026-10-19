import { useEffect, useState } from "react";
import { apiFetch, ApiRequestError } from "../../../api";

/** GET с отменой и защитой от запоздавшего ответа: результат принадлежит своему path (смена склада/вкладки/курсора
 *  не показывает чужие данные). 401/403/404 убирают прежние данные; сеть/5xx оставляют их с ошибкой. По образцу
 *  platform useApiRead — импорт из platform замкнул бы цикл через PlatformEntry. */
export type Read<T> = { data: T | null; error: string; loading: boolean; at: Date | null };

export function useRead<T>(path: string | null, reload = 0): Read<T> {
  const [state, setState] = useState<Read<T> & { path: string | null }>({ path, data: null, error: "", loading: Boolean(path), at: null });
  useEffect(() => {
    if (!path) { setState({ path, data: null, error: "", loading: false, at: null }); return; }
    const controller = new AbortController();
    setState(old => old.path === path ? { ...old, loading: true, error: "" } : { path, data: null, error: "", loading: true, at: null });
    apiFetch<T>(path, { signal: controller.signal })
      .then(data => { if (!controller.signal.aborted) setState({ path, data, error: "", loading: false, at: new Date() }); })
      .catch(reason => {
        if (controller.signal.aborted) return;
        const denied = reason instanceof ApiRequestError && [401, 403, 404].includes(reason.status);
        setState(old => denied || old.path !== path ? { path, data: null, error: text(reason), loading: false, at: null } : { ...old, loading: false, error: text(reason) });
      });
    return () => controller.abort();
  }, [path, reload]);
  return state.path === path ? state : { data: null, error: "", loading: Boolean(path), at: null };
}

function text(reason: unknown): string {
  if (!(reason instanceof ApiRequestError)) return "Нет связи с сервером — данные не получены.";
  if (reason.status === 401) return "Сессия завершена — войдите снова.";
  if (reason.status === 403) return "Нет права просмотра СНС/BLC на этом складе" + ".";
  if (reason.status === 404) return "Площадка или документ на этом складе не найдены" + ".";
  if (reason.status === 503) return "Сервер не подтвердил результат — повторите чтение позже" + ".";
  return "Не удалось получить данные. Обновите страницу.";
}
