import { useEffect, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../../api";
import { readError } from "../../access-admin";
import { RECOVERY_LIMIT, RecoveryShapeError, parseRecovery } from "./recoveryModel";
import type { RecoveryRow } from "./recoveryModel";

export type RecoveryRead = { rows: RecoveryRow[] | null; error: string; stale: boolean; loading: boolean; at: Date | null; denied: boolean };
type State = RecoveryRead & { key: string };

/** Чтение восстановления. warehouseId — выбранный склад (сменный обзор); "all" — все разрешённые склады (обзор директора).
 *  Ответ привязан к ключу (склад + пользователь): выборка прежнего склада/пользователя не показывается ни при загрузке, ни после.
 *  401/403/404 — данные скрываются; сеть/5xx — прежний снимок этого же ключа остаётся только с пометкой «устарел». */
export function useRecovery(warehouseId: string | "all" | null, scope: string, reload: number): RecoveryRead {
  const key = warehouseId ? `${scope}|${warehouseId}` : "";
  const [s, setS] = useState<State>({ key: "", rows: null, error: "", stale: false, loading: false, at: null, denied: false });
  useEffect(() => {
    if (!key) { setS({ key, rows: null, error: "", stale: false, loading: false, at: null, denied: false }); return; }
    const ctrl = new AbortController();
    setS(old => old.key === key ? { ...old, loading: true } : { key, rows: null, error: "", stale: false, loading: true, at: null, denied: false });
    const path = `/api/inventory/recovery-shorts?limit=${RECOVERY_LIMIT}${warehouseId !== "all" ? `&ware_id=${warehouseId}` : ""}`;
    apiFetch<unknown>(path, { signal: ctrl.signal })
      .then(v => { const rows = parseRecovery(v, warehouseId === "all" ? null : Number(warehouseId)); if (!ctrl.signal.aborted) setS({ key, rows, error: "", stale: false, loading: false, at: new Date(), denied: false }); })
      .catch(e => {
        if (ctrl.signal.aborted) return;
        const denied = e instanceof ApiRequestError && [401, 403, 404].includes(e.status);
        const error = e instanceof RecoveryShapeError ? e.message
          : denied && e.status === 403 ? "Нет права просматривать восстановление недостач на этом складе (case_pick_view)." : readError(e);
        setS(old => old.key !== key || denied || e instanceof RecoveryShapeError
          ? { key, rows: null, error, stale: false, loading: false, at: null, denied }
          : { ...old, loading: false, error, stale: old.rows !== null, denied: false });
      });
    return () => ctrl.abort();
  }, [key, reload]);
  const own = s.key === key;
  return own ? s : { rows: null, error: "", stale: false, loading: !!key, at: null, denied: false };
}
