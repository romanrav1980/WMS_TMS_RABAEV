import { useEffect, useRef } from "react";
import { apiFetch } from "../../api";

/** Read-only entry from the twin: resolve the exact trip, with the current actor's server admission. */
export function useTripDeepLink<T>(onOpen: (trip: T) => void, onError: (message: string) => void): void {
  const callbacks = useRef({ onOpen, onError });
  callbacks.current = { onOpen, onError };
  useEffect(() => {
    const id = new URLSearchParams(location.search).get("task_id");
    if (id === null) return;
    if (!/^[1-9][0-9]*$/.test(id) || !Number.isSafeInteger(Number(id))) {
      callbacks.current.onError("Некорректный номер рейса в ссылке.");
      return;
    }
    const controller = new AbortController();
    apiFetch<T>(`/api/admin/transport/tasks/${id}`, { signal: controller.signal })
      .then(trip => { if (!controller.signal.aborted) callbacks.current.onOpen(trip); })
      .catch(reason => { if (!controller.signal.aborted) callbacks.current.onError(`Рейс ${id} не открыт: ${String(reason)}`); });
    return () => controller.abort();
  }, []);
}
